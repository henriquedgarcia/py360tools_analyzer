from time import time
from tkinter import BooleanVar, StringVar, ttk
from typing import Iterator

import numpy as np
from PIL import Image, ImageTk
from py360tools import ProjectionBase, Tile, TileStitcher, Viewport

from lib.main import Main
from lib.mainappif import MainAppIf


class VideoControls:

    def play_pause(self):
        if not self.config:
            return

        if not self.running:
            self.running = True
            self.paused = False
            self.frame_time = 1000 / self.config.fps
            self.chunk = 1
            self._update_play_button(self.pause_icon)
            self.load_new_chunk()
            return

        if not self.paused:
            self.paused = True
            self._update_play_button(self.play_icon)
        else:
            self.paused = False
            self._update_play_button(self.pause_icon)
            self.video_loop()

    def rewind(self):
        self.chunk = 0
        if self.loop_id:
            self.app_root.after_cancel(self.loop_id)
            self.load_new_chunk()

    def stop(self):
        self.running = False
        self.paused = True
        self._update_play_button(self.play_icon)
        if self.loop_id:
            self.app_root.after_cancel(self.loop_id)
            self.viewport_label.imgtk = self.main_app.video_player.black_imgtk2
            self.projection_label.imgtk = self.main_app.video_player.black_imgtk1


class Controls(MainAppIf, VideoControls):
    """gerencia a quarta linha do aplicativo"""

    proj_obj: ProjectionBase
    viewport_obj: Viewport
    tiles_seen: list[Tile]
    tiles_seen_ref: list[Tile]
    chunk_hmd_samples_iter: iter

    frame_iterator: Iterator[np.ndarray]
    frame_iterator_ref: Iterator[np.ndarray]

    bitrate = int
    n_tiles = int

    pause_icon: StringVar
    play_icon: StringVar
    rewind_icon: StringVar
    stop_icon: StringVar
    repeat: BooleanVar
    button_dict: dict[str, ttk.Button | ttk.Checkbutton]
    control_frame: ttk.LabelFrame

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self._set_variables()
        self._create_control_frame()
        self._create_buttons()

    # noinspection PyTypeChecker
    def _set_variables(self):
        self.play_icon = StringVar()
        self.play_icon.set("\u25B6")
        self.pause_icon = StringVar()
        self.pause_icon.set("\u23F8")
        self.rewind_icon = StringVar()
        self.rewind_icon.set("\u23EE")
        self.stop_icon = StringVar()
        self.stop_icon.set("\u23F9")

        self.repeat = BooleanVar()
        self.repeat.set(False)

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
                            }
        for column, button in enumerate(self.button_dict.values()):
            button.grid(row=0, column=column, padx=5, sticky='ew')

    def load_new_chunk(self):
        start_time = time()

        self._update_state()
        self._update_tiles_seen_chunk()
        self._update_tiles_path()
        self._update_tile_stitcher()  # O buffer pode vir aqui
        self._update_chunk_graphs(start_time)

        # calcula o tempo do pré-processamento e desconta ele do agendador de frame.
        # se tiver passado de 33ms (1/fps) executa o loop imediatamente
        print(f'pre-process time is {self.dectime}ms')
        diff = self.frame_time - self.dectime
        diff = diff if diff > 0 else 1

        # noinspection PyTypeChecker
        self.app_root.after(int(diff), self.video_loop)

        # Inicializa vídeo
        #     calcula bitrate e n_tiles deste chunk
        ...
        # atualize gráfico 1
        #     taxa de bits, n_tiles, tempo de pre-processamento, tiles MSE, chunk MSE
        ...
        # faz a reprodução deste tilestitcher (loop de vídeo do chunk)
        #     next tilestitcher (se acabou lançará um StopIteration)
        #     next tilestitcher_ref (se acabou lançará um StopIteration)
        #     next viewport position.
        #     ...
        #     extraia o viewport
        #     extraia o viewport_ref
        #
        #     redimensione frame e viewport
        #     (não corrige cor porque estamos fazendo tudo em p/b)
        #
        #     converta para Image
        #     Converta para PhotoImage
        #     atribua ao label do vídeo equivalente
        #
        #     atualize gráfico 2
        #     agende o after para 1/fps segundos

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
        chunk_hmd_samples = self.user_movement[frame_ini:frame_end].values
        self.chunk_hmd_samples_iter = iter(chunk_hmd_samples)

        ypr = self.viewport_obj.yaw_pitch_roll
        tiles_seen = set()
        for yaw_pitch_roll in chunk_hmd_samples:
            sees = self.viewport_obj.get_vptiles(yaw_pitch_roll)
            tiles_seen.update(sees)
        self.tiles_seen = list(tiles_seen)
        self.tiles_seen_ref = self.tiles_seen.copy()
        self.viewport_obj.yaw_pitch_roll = ypr

    def _update_tiles_path(self):
        for self.tile, self.tile_ref in zip(self.tiles_seen, self.tiles_seen_ref):
            q = self.quality

            self.quality = 0
            self.tile_ref.path = self.chunk_path

            self.quality = q
            self.tile.path = self.chunk_path

    def _update_tile_stitcher(self):
        proj_stitcher = TileStitcher(tiles_seen=self.tiles_seen,
                                     proj_obj=self.proj_obj)
        proj_stitcher_ref = TileStitcher(tiles_seen=self.tiles_seen_ref,
                                         proj_obj=self.proj_obj)
        self.frame_iterator = iter(proj_stitcher)
        self.frame_iterator_ref = iter(proj_stitcher_ref)

    def _update_chunk_graphs(self, start):
        self.dectime = (time() - start)  #
        self.bitrate = sum(tile.path.stat().st_size for tile in self.tiles_seen)
        self.n_tiles = len(self.tiles_seen)

    def _update_play_button(self, value: StringVar):
        self.button_dict['play_pause'].config(textvariable=value)

    def video_loop(self):
        start = time()
        if self.running and not self.paused:
            try:
                frame = next(self.frame_iterator)
                yaw_pitch_roll = next(self.chunk_hmd_samples_iter)
            except StopIteration:
                self._finish_chunk()
                return
            frame_time = time()
            # projeção
            mask = self.viewport_obj.draw_mask(255)
            frame2 = 0.5 * frame + 0.5 * mask

            img = Image.fromarray(frame2)
            if self.projection == 'cmp':
                img = img.resize((360, 240))
            else:
                img = img.resize((480, 240))

            imgtk = ImageTk.PhotoImage(image=img)
            self.projection_label.imgtk = imgtk
            # noinspection PyTypeChecker
            self.projection_label.configure(image=imgtk)

            # viewport
            viewport_frame = self.viewport_obj.extract_viewport(frame, yaw_pitch_roll)
            img = Image.fromarray(viewport_frame)
            img = img.resize((310, 230))
            imgtk = ImageTk.PhotoImage(image=img)
            self.viewport_label.imgtk = imgtk
            # noinspection PyTypeChecker
            self.viewport_label.configure(image=imgtk)

            # frame_ref = next(self.frame_iterator_ref)
            # self.proj_mse_value = mse(frame, frame_ref)
            # self.proj_ssim_value = ssim(frame, frame_ref)

            # viewport_frame_ref = self.viewport_obj.extract_viewport(frame_ref, yaw_pitch_roll)
            # self.viewport_mse_value = mse(viewport_frame, viewport_frame_ref)
            # self.viewport_ssim_value = ssim(viewport_frame, viewport_frame_ref)

            # noinspection PyTypeChecker
            proc_time = (time() - start) / 1000000  # ns to ms
            diff = self.frame_time - proc_time
            diff = diff if diff > 0 else 0
            print(f'frame process time is {time() - frame_time: 0.3f}s')
            self.loop_id = self.app_root.after(int(diff), self.video_loop)
            # self.loop_id = self.app_root.after(int(1), self.video_loop)

    def _finish_chunk(self):
        self.chunk += 1
        if self.chunk > 60:
            self.rewind()
            if not self.repeat.get():
                self.stop()
                return
        # noinspection PyTypeChecker
        self.app_root.after(0, self.load_new_chunk)

    loop_id: int = None
