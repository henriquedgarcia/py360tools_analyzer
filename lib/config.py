import json
from functools import cached_property
from pathlib import Path
from typing import Union

import pandas as pd
from py360tools import ERP, CMP


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

    get_user_movement(video: str, user: int) -> pd.DataFrame
        Retrieves user-specific head movement data for a specified video.
    """
    config: dict[str, Union[int, str, list[str]]]

    proj_type = {'erp': ERP, 'cmp': CMP}

    def __init__(self, config_file: Path):
        self.config = json.loads(config_file.read_text())

        self.video: str = self.config['video']
        self.projection: str = self.config['projection']
        self.tiling: str = self.config['tiling']
        self.resolution: str = self.config['resolution']
        self.fov: str = self.config['fov']
        self.duration: int = self.config['duration']
        self.fps: int = self.config['fps']
        self.quality_list: list[str] = self.config['quality_list']
        self.segment_template: str = self.config['segment_template']
        self.head_movement_filename = Path(self.config['head_movement_filename'])

        self.fov_x, self.fov_y = map(int, self.fov.split('x'))
        self.shape = tuple(map(int, self.resolution.split('x')))[::-1]
        self.n_frames = self.duration * self.fps
        self.fov_resolution = f'{int(round(self.shape[1]*(self.fov_x / self.fov_y)))}x{self.shape[1]}'

    @staticmethod
    def get_tile_list(tiling: str) -> list:
        x, y = tiling.split('x')
        return list(range(int(x) * int(y)))

    @cached_property
    def head_movement_data(self) -> pd.DataFrame:
        return pd.read_hdf(self.head_movement_filename)

    def get_user_movement(self, video: str, user: int) -> pd.DataFrame:
        return self.head_movement_data.loc[(video, user)]
