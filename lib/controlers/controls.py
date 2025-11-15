from collections.abc import Callable
from pathlib import Path
from time import time
from tkinter import BooleanVar, StringVar, ttk
from typing import Iterator, Optional

import numpy as np
from PIL import Image, ImageTk
from py360tools import TileStitcher
from skimage.metrics import mean_squared_error

from lib.main import Main
from lib.mainappif import ComboIf, ControlsIf, GraphsIf, MainAppIf, PlayerIf


class GraphsControls(GraphsIf, MainAppIf):
    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self.graphs_reset()


class NewChunk(MainAppIf, ComboIf):
    frame_time: float
    dectime: float
    video_loop: Callable

    chunk_hmd_samples_iter: Iterator
    frame_iterator: Iterator[np.ndarray]
    frame_iterator_ref: Iterator[np.ndarray]

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self.graphs_controls = GraphsControls(self.main_app)

    def __call__(self):
        """
        A função time() aqui calcula o tempo do pré-processamento e desconta ele
        do agendador de frame. se tiver passado de 33ms (1/30fps) executa o loop
        imediatamente
        """
        if not self.running: return
        start_time = time()

        self._update_state()
        self._update_tiles_seen_chunk()
        self._update_tiles_path()
        self._update_tile_stitcher()  # O buffer pode vir aqui
        self._update_graphs_chunk()

        dectime = (time() - start_time)
        print(f'pre-process time is {dectime}ms')
        diff = self.frame_time - dectime
        diff = diff if diff > 0 else 0
        self.app_root.after(int(diff), self.video_loop)

    def _update_state(self):
        self.quality = int(self.combo_dict['quality'].get())
        self.user = int(self.combo_dict['user'].get())

    def _update_tiles_seen_chunk(self):
        """
        pegamos 30 amostras de movimento de cabeça (30 frames == gop == chunk)
        pegamos os tiles vistos para cada uma das 30 amostra a botamos em um set()
            com isto teremos todos os tiles que foram vistos durante o chunk
        usamos esse set para criar duas listas de tiles vistos:
            uma será usada para os tiles de referência (lossless)
            outra será usda para os tiles degradados (QP variado)
        Criamos um iterador com as amostras de cabeça
        """
        frame_ini = (self.chunk - 1) * self.config.fps
        frame_end = frame_ini + self.config.fps
        chunk_hmd_predicted = self.user_movement[frame_ini:frame_end].values
        self.chunk_hmd_samples_iter = iter(chunk_hmd_predicted)

        ypr = self.viewport_obj.yaw_pitch_roll

        tiles_seen = set()
        for yaw_pitch_roll in chunk_hmd_predicted:
            sees = self.viewport_obj.get_vptiles(yaw_pitch_roll)
            tiles_seen.update(sees)

        self.tiles_seen = [tile.idx for tile in tiles_seen]
        self.viewport_obj.yaw_pitch_roll = ypr
        self.viewport_obj_ref.yaw_pitch_roll = ypr

    def _update_tiles_path(self):
        for self.tile in self.tiles_seen:
            q = self.quality
            self.quality = 0

            self.proj_obj.tile_list[self.tile].path = self.chunk_path
            self.tile_ref.path = self.chunk_path

            self.quality = q
            self.tile.path = self.chunk_path

    def _update_tile_stitcher(self):
        self.proj_stitcher = TileStitcher(tiles_seen=self.tiles_seen,
                                          proj_obj=self.proj_obj)
        self.proj_stitcher_ref = TileStitcher(tiles_seen=self.tiles_seen,
                                              proj_obj=self.proj_obj)
        self.frame_iterator = iter(self.proj_stitcher)
        self.frame_iterator_ref = iter(self.proj_stitcher_ref)

    proj_mse_list: Optional[list[float]] = None
    viewport_mse_list: Optional[list[float]] = None

    def _update_graphs_chunk(self):
        bitrate = sum(tile.path.stat().st_size for tile in self.tiles_seen) / 1000000
        n_tiles = len(self.tiles_seen)

        proj_mse_value = np.average(self.proj_mse_list)
        viewport_mse_value = np.average(self.viewport_mse_list)

        self.proj_mse_list.clear()
        self.viewport_mse_list.clear()

        self.graphs_controls.update_graphs_chunk(bitrate, n_tiles)
        self.graphs_controls.update_graphs_frame(proj_mse_value, viewport_mse_value)

    @property
    def chunk_path(self) -> Path:
        kwargs = dict(video=self.video, projection=self.projection,
                      tiling=self.tiling, quality=self.quality,
                      tile=self.tile, chunk=self.chunk)
        return Path(self.config.segment_template.format(**kwargs))


class VideoLoop(MainAppIf, PlayerIf, ControlsIf):
    disable_video: BooleanVar
    frame_time: float

    def __init__(self, main_app: Main):
        super().__init__(main_app)

    def __call__(self):
        if not self.running or self.paused: return

        start_time = time()
        if not self.disable_video.get():
            self.update_proj_frame()
            if self.proj_frame is None: return

            self.update_yaw_pitch_roll()
            self.make_projection_masked_img()
            self.plot_projection_masked_img()
            self.make_viewport_img()
            self.plot_viewport_img()
        self.update_graphs_frame()

        # noinspection PyTypeChecker
        proc_time = (time() - start_time)
        # print(f'frame process time is {proc_time: 0.3f}s')

        diff = (0 if proc_time > self.frame_time
                else int(self.frame_time - proc_time))

        self.loop_id = self.app_root.after(diff, self)

    frame_iterator: Iterator[np.ndarray]
    proj_frame: Optional[np.ndarray]

    def update_proj_frame(self):
        try:
            self.proj_frame = next(self.frame_iterator)
        except StopIteration:
            self.finish_chunk()  # End of chunk
            self.proj_frame = None

    chunk_hmd_samples_iter: Iterator

    def update_yaw_pitch_roll(self):
        yaw_pitch_roll: tuple[float, float, float]
        try:
            yaw_pitch_roll = next(self.chunk_hmd_samples_iter)
        except StopIteration:
            self.finish_chunk()  # End of chunk
            return None
        self.viewport_obj.yaw_pitch_roll = yaw_pitch_roll
        self.viewport_obj_ref.yaw_pitch_roll = yaw_pitch_roll
        return True

    projection_masked_img: Image.Image

    def make_projection_masked_img(self):
        mask = self.viewport_obj.draw_mask(255)
        frame_masked = 0.5 * self.proj_frame + 0.5 * mask
        self.projection_masked_img = Image.fromarray(frame_masked)

    def plot_projection_masked_img(self):
        imgtk = ImageTk.PhotoImage(image=self.projection_masked_img)
        self.projection_label.imgtk = imgtk
        # noinspection PyTypeChecker
        self.projection_label.configure(image=imgtk)

    viewport_frame: np.ndarray
    viewport_img: Image.Image

    def make_viewport_img(self):
        self.viewport_frame = self.viewport_obj.extract_viewport(self.proj_frame, self.viewport_obj.yaw_pitch_roll)
        self.viewport_img = Image.fromarray(self.viewport_frame)

    def plot_viewport_img(self):
        imgtk = ImageTk.PhotoImage(image=self.viewport_img)
        self.viewport_label.imgtk = imgtk
        self.viewport_label.configure(image=imgtk)

    def update_graphs_frame(self):
        self.get_references()
        self.get_mse()
        # self.graphs_controls.update_graphs_frame(self.viewport_mse_list, self.proj_mse_list)
        # self.frame += 1

    viewport_frame_ref: np.ndarray
    frame_ref: np.ndarray
    frame_iterator_ref: Iterator[np.ndarray]

    def get_references(self):
        self.frame_ref = next(self.frame_iterator_ref)
        self.viewport_frame_ref = self.viewport_obj_ref.extract_viewport(self.frame_ref)

    proj_stitcher: TileStitcher
    proj_stitcher_ref: TileStitcher
    proj_mse_list: Optional[list[float]] = None
    viewport_mse_list: Optional[list[float]] = None

    def get_mse(self):
        tiles = zip(self.proj_stitcher.proj_obj.tile_list,
                    self.proj_stitcher_ref.proj_obj.tile_list)
        mse_list = []
        for tile, tile_ref in tiles:
            if tile.idx in self.proj_stitcher.tiles_seen:
                mse_list.append(mean_squared_error(tile.canvas, tile_ref.canvas))

        self.proj_mse_list.append(float(np.average(mse_list)))

        viewport_mse_value = mean_squared_error(self.viewport_frame, self.viewport_frame_ref)
        self.viewport_mse_list.append(viewport_mse_value)

    new_chunk: Callable

    def finish_chunk(self):
        self.chunk += 1

        if self.chunk > self.config.n_chunks:
            if not self.main_app.controls.repeat.get():
                self.main_app.controls.stop()
            else:
                self.main_app.controls.rewind()

        self.app_root.after(0, self.new_chunk)


class VideoControls(MainAppIf, PlayerIf, GraphsIf, ControlsIf):
    play_icon = StringVar(value="\u25B6")
    pause_icon = StringVar(value="\u23F8")
    rewind_icon = StringVar(value="\u23EE")
    stop_icon = StringVar(value="\u23F9")

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self.new_chunk = NewChunk(self.main_app)
        self.video_loop = VideoLoop(self.main_app)

    def play_pause(self):
        if not self.config:
            print('Carregue um arquivo de configuração primeiro!')
            return

        if self.running:
            if self.paused:
                self._update_play_button(self.pause_icon)
                self.paused = False
                self.app_root.after(0, self.video_loop)
            else:
                self._update_play_button(self.play_icon)
                self.paused = True

        else:
            self._update_play_button(self.pause_icon)
            self.running = True
            self.paused = False
            self.chunk = 1
            self.frame = 0
            self.graphs_reset()

            self.new_chunk()

    def rewind(self):
        self.stop()
        self.play_pause()

    def stop(self):
        self.running = False
        self.paused = True
        self._update_play_button(self.play_icon)

        self.viewport_label.imgtk = self.main_app.video_player.black_imgtk2
        self.projection_label.imgtk = self.main_app.video_player.black_imgtk1

    def _update_play_button(self, value: StringVar):
        self.button_dict['play_pause'].config(textvariable=value)


class Controls(MainAppIf):
    """gerencia a quarta linha do aplicativo"""
    control_frame: ttk.LabelFrame

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self._set_variables()
        self._create_control_frame()
        self._create_buttons()

    # noinspection PyTypeChecker
    def _set_variables(self):

        self.repeat = BooleanVar()
        self.repeat.set(False)
        self.disable_video = BooleanVar()
        self.disable_video.set(False)

        self.video_controls = VideoControls(self.main_app)

    def _create_control_frame(self):
        self.control_frame = ttk.LabelFrame(self.app_root, text='Controles')
        self.control_frame.grid(row=3, column=0, padx=5, pady=5)
        self.control_frame.grid_rowconfigure(0, weight=0)

        for i in range(4):
            self.control_frame.grid_columnconfigure(i, weight=0)

    def _create_buttons(self):
        self.button_dict = {'play_pause': ttk.Button(self.control_frame, text='\u25B6',
                                                     command=self.play_pause),
                            'rewind': ttk.Button(self.control_frame, text='\u23EE',
                                                 command=self.rewind),
                            'stop': ttk.Button(self.control_frame, text='\u23F9',
                                               command=self.stop),
                            'repeat': ttk.Checkbutton(self.control_frame, text='Repeat',
                                                      variable=self.repeat),
                            'disable_video': ttk.Checkbutton(self.control_frame, text='Disable Video',
                                                             variable=self.disable_video),
                            }
        for column, button in enumerate(self.button_dict.values()):
            button.grid(row=0, column=column, padx=5, sticky='ew')

    @property
    def play_pause(self) -> Callable:
        return self.video_controls.play_pause

    @property
    def rewind(self) -> Callable:
        return self.video_controls.rewind

    @property
    def stop(self) -> Callable:
        return self.video_controls.stop
