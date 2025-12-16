from pathlib import Path
from tkinter import filedialog, ttk
from typing import Optional

import numpy as np
from py360tools import AutoDict, Projection, Tile, TileStitcher, Viewport
from skimage.metrics import mean_squared_error, structural_similarity

from lib.interfaces.mainappif import MainAppIf
from lib.main import Main


class OpenControl(MainAppIf):
    def open(self):
        debug = True
        if debug:
            json_path = Path('./config/config_test1.json')
        else:
            json_path = filedialog.askopenfilename(title='Selecione um arquivo',
                                                   initialdir='./config/',
                                                   filetypes=[('application/json', '*.json')])
            json_path = Path(json_path)
        self.console.print_console(f"Opening config: {json_path}")
        self.config.open(json_path)


class SaveControl(MainAppIf):
    def save(self): ...


class CleanControl(MainAppIf):
    def clean(self): ...


class StopControl(MainAppIf):
    def stop(self): ...


class StatsIf(MainAppIf):
    @property
    def video(self):
        return self.state.video

    @video.setter
    def video(self, value):
        self.menu.update_labels_frame('video', str(value))
        self.state.video = value

    @property
    def projection(self):
        return self.state.projection

    @projection.setter
    def projection(self, value):
        self.menu.update_labels_frame('projection', str(value))
        self.state.projection = value

    @property
    def tiling(self):
        return self.state.tiling

    @tiling.setter
    def tiling(self, value):
        self.menu.update_labels_frame('tiling', str(value))
        self.state.tiling = value

    @property
    def quality(self):
        return self.state.quality

    @quality.setter
    def quality(self, value):
        self.menu.update_labels_frame('quality', str(value))
        self.state.quality = value

    @property
    def tile(self):
        return self.state.tile

    @tile.setter
    def tile(self, value):
        self.state.tile = value

    @property
    def user(self):
        return self.state.user

    @user.setter
    def user(self, value):
        self.menu.update_labels_frame('user', str(value))
        self.state.user = value

    @property
    def chunk(self):
        return self.state.chunk

    @chunk.setter
    def chunk(self, value):
        self.menu.update_labels_frame('chunk', str(value))
        self.state.chunk = value

    @property
    def metric(self):
        return self.state.metric

    @metric.setter
    def metric(self, value):
        self.menu.update_labels_frame('metric', str(value))
        self.state.metric = value


class StartControl(StatsIf, MainAppIf):
    chunk_stats: AutoDict

    project_obj: Projection
    project_obj_ref: Projection

    viewport_obj: Viewport
    viewport_obj_ref: Viewport

    tiles_seen_chunk: list[Tile]
    tiles_seen_chunk_ref: list[Tile]

    proj_stitcher: TileStitcher
    proj_stitcher_ref: TileStitcher

    def start(self):
        self.console.print_console(f"Starting analysis...")
        self.configure_environment()
        self.check_hmd()
        self.run_loop()

    def configure_environment(self):
        self.chunk_stats = AutoDict()

    def check_hmd(self):
        """
        + verificar se o dataset HMD
            - possui os vídeos em questão,
            - tem o formato correto (3 colunas 'yaw', 'pitch', 'roll')
            - só possui dois três níveis ('name', 'user', 'frame')

        """
        hmd_videos = self.config.head_movement_data.index.unique('video')
        for video in self.config.video_list:
            if video not in hmd_videos:
                raise ValueError(f"Video {video} not found in head movement data")
        return 'ok'

    metrics_obj: 'Metrics'

    def run_loop(self):
        """
        + verificar arquivos de vídeo existem
            - fazer um LOOP e procurar todos os chunks se existem no formato:
            self.config.segment_template.format(video, projection, tiling,
            tile, quality, chunk)

        Sim. verificar todos agora. A saída precisa de todos os dados.
        """

        self.metrics_obj = Metrics(self)
        for self.video in self.config.video_list:
            for self.projection in self.config.projection_list:
                for self.tiling in self.config.tiling_list:
                    self._update_proj_obj()
                    self._update_viewport_obj()

                    try:
                        self._check_chunks()
                    except FileNotFoundError:
                        self.console.print_console(f"Chunk {self.chunk_path} not found")
                        continue

                    for self.user in self.config.get_user_list(self.state.video):
                        # Sessão do usuário user tem os frames de cada qualidade
                        for self.chunk in self.config.chunk_list:
                            self._update_hmd_data_chunk()  # preditor de viewport
                            self._update_tiles_seen_chunk()  # Seletor de ladrilhos

                            self._update_tile_stitcher_ref()  # Referencia
                            for self.quality in self.config.quality_list:
                                self._check_metrics_existence()
                                self._update_tiles_path()  # Seletor de qualidade cte.
                                self._update_tile_stitcher()  # Decodificador e remontador
                                self._frame_loop()
                                self._get_chunk_metrics()

    def _check_metrics_existence(self):
        ...

    def _get_chunk_metrics(self):
        """
        toda métrica deve ser validada e salva no caminho temporário
        self.config.project_folder /{video}{usuário}{projeção}{tiling}{quality}{chunk}
        """
        for metric, var in self.main_app.checkboxes.checkbox_var_dict.items():
            if var.get() is False: continue
            getattr(self.metrics_obj, f'get_{metric}')()

        """	/- bitrate
            /- n_tiles_seen
            /- avg_tile_mse
            /- avg_viewport_mse
            /- avg_tile_ssim
            /- avg_viewport_ssim
            
            /- avg_tile_s_mse
            /- avg_tile_ws_mse
        """

    def _update_proj_obj(self):
        self.project_obj = self.config.create_projection(self.state.projection, self.state.tiling)
        self.project_obj_ref = self.config.create_projection(self.state.projection, self.state.tiling)

    def _update_viewport_obj(self):
        self.viewport_obj = Viewport(self.config.fov_resolution, self.config.fov, self.project_obj)
        self.viewport_obj_ref = Viewport(self.config.fov_resolution, self.config.fov, self.project_obj)

    def _check_chunks(self):
        self.console.print_console(f"Checking video: [{self.video}][{self.projection}][{self.tiling}]")
        self.metric = 'check_chunks'
        for self.tile in self.project_obj.tile_list:
            for self.quality in self.config.quality_list:
                for self.chunk in self.config.chunk_list:
                    if not self.chunk_path.exists():
                        raise FileNotFoundError(f"Chunk {self.chunk_path} not found")
        return

    def _update_hmd_data_chunk(self):
        frame_ini = (self.state.chunk - 1) * self.config.fps
        frame_end = frame_ini + self.config.fps
        self.hmd_data_chunk = self.user_movement[frame_ini:frame_end].values

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
        tiles_seen: set[Tile] = set()
        tiles_seen_ref: set[Tile] = set()

        ypr = self.viewport_obj.yaw_pitch_roll
        for yaw_pitch_roll in self.hmd_data_chunk:
            sees = self.viewport_obj.get_vptiles(yaw_pitch_roll)
            sees_ref = self.viewport_obj_ref.get_vptiles(yaw_pitch_roll)
            tiles_seen.update(sees)
            tiles_seen_ref.update(sees_ref)
        self.viewport_obj.yaw_pitch_roll = ypr
        self.viewport_obj_ref.yaw_pitch_roll = ypr

        self.tiles_seen_chunk = list(tiles_seen)
        self.tiles_seen_chunk_ref = list(tiles_seen_ref)

    def _update_tiles_path(self):
        for self.tile in self.tiles_seen_chunk:
            self.state.tile.path = self.chunk_path

    def _update_tile_stitcher(self):
        self.proj_stitcher = TileStitcher(tiles_seen=self.tiles_seen_chunk,
                                          proj_obj=self.project_obj)

    def _update_tile_stitcher_ref(self):
        self.proj_stitcher_ref = TileStitcher(tiles_seen=self.tiles_seen_chunk_ref,
                                              proj_obj=self.project_obj_ref)
        q = self.state.quality
        self.state.quality = 0
        for tile_ref in self.tiles_seen_chunk_ref:
            tile_ref.path = self.chunk_path
        self.state.quality = q

    def _frame_loop(self):
        self.tiles_mse_list = []
        self.tiles_ssim_list = []
        self.viewport_mse_list = []
        self.viewport_ssim_list = []

        zip_frame = zip(self.proj_stitcher, self.proj_stitcher_ref, self.hmd_data_chunk)
        for frame, frame_ref, yaw_pitch_roll in zip_frame:
            self.viewport = self.viewport_obj.extract_viewport(frame, yaw_pitch_roll)
            self.viewport_ref = self.viewport_obj_ref.extract_viewport(frame_ref, yaw_pitch_roll)

            self.get_frame_quality()

    tiles_mse_list: Optional[list[float]] = None
    tiles_ssim_list: Optional[list[float]] = None
    viewport_mse_list: Optional[list[float]] = None
    viewport_ssim_list: Optional[list[float]] = None
    chunk_hmd_samples: list[tuple[float, float, float]] = []

    def get_frame_quality(self):
        tiles_seen = zip(self.proj_stitcher.tiles_seen,
                         self.proj_stitcher_ref.tiles_seen)

        for metric, var in self.main_app.checkboxes.checkbox_var_dict.items():
            if var.get() is False: continue
            if metric == 'n_tiles': continue
            if metric == 'bitrate': continue
            getattr(self.metrics_obj, f'get_{metric}')()

        ############## tiles_mse #####################
        tiles_mse_list = [mean_squared_error(tile.canvas, tile_ref.canvas)
                          for tile, tile_ref in tiles_seen]
        tiles_mse_value = float(np.average(tiles_mse_list))
        self.tiles_mse_list.append(tiles_mse_value)

        ############## tiles_ssim #####################
        tiles_ssim_list = [structural_similarity(tile.canvas, tile_ref.canvas)
                           for tile, tile_ref in tiles_seen]
        tiles_ssim_value = float(np.average(tiles_ssim_list))
        self.tiles_ssim_list.append(tiles_ssim_value)

        ############### viewport_mse ####################
        viewport_mse_value = mean_squared_error(self.viewport, self.viewport_ref)
        self.viewport_mse_list.append(viewport_mse_value)

        ############### viewport_ssim ####################
        viewport_ssim_value = structural_similarity(self.viewport, self.viewport_ref)
        self.viewport_ssim_list.append(viewport_ssim_value)

    @property
    def chunk_path(self):
        chunk_path = self.config.get_segment_path(self.video,
                                                  self.projection,
                                                  self.tiling,
                                                  self.tile,
                                                  self.quality,
                                                  self.chunk)
        return chunk_path


class Metrics:
    def __init__(self, control: StartControl):
        self.control = control
        ...

    def get_n_tiles(self):
        n_tiles = len(self.control.tiles_seen_chunk)
        return n_tiles

    def get_bitrate(self):
        bitrate = sum(tile.path.stat().st_size for tile in self.control.tiles_seen_chunk) / 1000000
        return bitrate

    def get_avg_tile_mse(self):
        tile_mse_value = np.average(self.control.tiles_mse_list)
        self.control.tiles_mse_list.clear()
        return tile_mse_value

    def get_avg_viewport_mse(self):
        viewport_mse_value = np.average(self.control.viewport_mse_list)
        self.control.viewport_mse_list.clear()
        return viewport_mse_value


class Controls(OpenControl, SaveControl, StartControl, StopControl, CleanControl):
    """gerencia a quarta linha do aplicativo"""
    control_frame: ttk.LabelFrame

    def __init__(self, main_app: Main):
        super().__init__(main_app)
