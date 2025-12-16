import json
from pathlib import Path
from typing import Type, Union

import pandas as pd
from py360tools import CMP, ERP, Projection, splitx, Viewport


class Config:
    """
    Represents a configuration for this project.

    This class is responsible for loading and managing the configuration settings
    configuration file. The configuration covers various parameters like video settings, projection details,
    tiling information, resolution, field of view, frame rate, quality levels, and user movement data. It also
    provides helper methods for processing tiling details and accessing user-specific head movement data.

    Attributes
    ----------
    config : dict[str, Union[int, str, list[str]]]
        Dictionary containing the project configuration settings.
    proj_type : dict[str, type]
        Mapping of projection types to their corresponding classes.

    Parameters
    ----------
    config_file : Path
        Path to the JSON configuration file.

    Methods
    -------
    get_tile_list(tiling: str) -> list
        Static method returning a list of tile indices based on a tiling string.

    head_movement_data : pd.DataFrame
        Cached property loading user head movement data into a DataFrame.

    Get_user_movement(video: str, user: int) -> pd.DataFrame
        Retrieves user-specific head movement data for a specified video.
    """
    hash: int
    config: dict[str, Union[int, str, list[str]]] | None

    proj_type: dict[str, Type[Projection]] = {'erp': ERP, 'cmp': CMP}

    video_list: list[str]
    projection_list: list[str]
    tiling_list: list[str]
    quality_list: list[int]
    chunk_list: list[int]
    rate_control: str
    resolution: str
    fov_resolution: str
    fov: str
    duration: int
    fps: int
    gop: int
    segment_template: str
    head_movement_filename: Path

    head_movement_data: pd.DataFrame

    fov_x: int
    fov_y: int
    shape: tuple[int, int]
    shape_x: int
    shape_y: int
    n_frames: int
    frame_time: float
    chunk_time: float
    project_folder: Path

    def __init__(self, config_file: Path = None):
        if config_file is None:
            self.config = None
            return

        self.open(config_file)

    def open(self, config_file: Path):
        """
        cadeia de eventos:
            - abrir arquivo
            - converter valores do json em atributos
            - Abrir o dataset de movimento de cabeça.
            - pre-calcular shape, numero de frames, duração do frame, duração do
            chunk, etc.
            -pre-calcular lista de usuários por video
            -pre-calcular posição e tamanho dos tiles por projeção e tiling
        """
        config_text = config_file.read_text()
        project_name = hash(config_text).to_bytes(8, signed=True, byteorder="big").hex()
        self.project_folder = Path(f'./cache/{project_name}')
        self.project_folder.mkdir(parents=True, exist_ok=True)

        self.config = json.loads(config_text)

        self.video_list: list[str] = self.config['video_list']
        self.projection_list: list[str] = self.config['projection_list']
        self.tiling_list: list[str] = self.config['tiling_list']
        self.quality_list: list[str] = self.config['quality_list']
        self.rate_control: str = self.config['rate_control']
        self.resolution: str = self.config['resolution']
        self.fov_resolution: str = self.config['fov_resolution']
        self.fov: str = self.config['fov']
        self.duration: int = self.config['duration']
        self.fps: int = self.config['fps']
        self.gop: int = self.config['fps']
        self.segment_template: str = self.config['segment_template']
        self.head_movement_filename = Path(self.config['head_movement_filename'])

        self.head_movement_data = pd.read_hdf(self.head_movement_filename)

        self.fov_x, self.fov_y = splitx(self.fov)
        self.shape_x, self.shape_y = splitx(self.resolution)
        self.shape = self.shape_y, self.shape_x
        self.n_frames = self.duration * self.fps
        self.frame_time = 1000 / self.fps
        self.chunk_time = 1000 * self.gop / self.fps
        self.chunk_list = list(range(1, self.n_frames // self.gop + 1))

    def get_users_list(self, video) -> list[int]:
        dados_filtrados = self.head_movement_data.loc[(video,)]
        users_list = list(dados_filtrados.index.unique('user'))
        return users_list

    proj_obj: Projection
    viewport_obj: Viewport

    def create_projection(self, projection: str, tiling: str) -> Projection:
        proj = self.proj_type[projection]
        self.proj_obj = proj(proj_res=self.resolution, tiling=tiling)
        return self.proj_obj

    def create_viewport(self, proj_obj: Projection):
        self.viewport_obj = Viewport(resolution=self.fov_resolution,
                                     fov=self.fov, projection=proj_obj)
        return

    def get_segment_path(self, video, projection, tiling, tile, quality, chunk):
        chunk_path = self.segment_template.format(video=video, projection=projection, tiling=tiling, tile=tile, quality=quality, chunk=chunk)
        return Path(chunk_path)

    @staticmethod
    def get_tile_list(tiling: str) -> list:
        x, y = tiling.split('x')
        return list(range(int(x) * int(y)))

    def get_user_movement(self, video: str, user: int) -> pd.DataFrame:
        return self.head_movement_data.loc[(video, user)]
