import json
from functools import cached_property
from pathlib import Path

import pandas as pd
from py360tools import splitx


class Config:
    config: dict

    video_list: list[str]
    projection_list: list[str]
    tiling_list: list[str]
    quality_list: list[str]

    head_movement_filename: str
    tiles_seen_filename: str
    viewport_quality_filename: str
    chunk_data_filename: str

    def __init__(self, config_file: Path):
        self.config = json.loads(config_file.read_text())

        self.codec = self.config['codec']
        self.duration = self.config['duration']
        self.fps = self.config['fps']
        self.gop=self.fps
        self.fov=self.config['fov']
        self.fov_x, self.fov_y = splitx(self.fov)
        self.n_frames = self.duration * self.fps
        self.resolution = self.config['resolution']
        self.erp_resolution = f'{int(2* self.resolution)}x{self.resolution}'
        self.cmp_resolution = f'{int(3* self.resolution/2)}x{self.resolution}'
        self.fov_resolution = f'{int(110* self.resolution/90)}x{self.resolution}'

        self.video_list = self.config['video_list']
        self.projection_list = self.config['projection_list']
        self.tiling_list = self.config['tiling_list']
        self.quality_list = self.config['quality_list']

        self.media_template = self.config['media_template']
        self.head_movement_filename = self.config['head_movement_filename']

    @staticmethod
    def get_tile_list(tiling: str) -> list:
        x, y = tiling.split('x')
        return list(range(int(x) * int(y)))

    @cached_property
    def head_movement_data(self) -> pd.DataFrame:
        return pd.read_hdf(self.head_movement_filename)

    def get_user_movement(self, video: str, user: int)-> pd.DataFrame:
        return self.head_movement_data.loc[(video, user)]
