from pathlib import Path
from tkinter import StringVar

from py360tools import ProjectionBase, Tile, Viewport

from lib.config import Config
from lib.main import Main


class StateIf:
    main_app: Main
    config: Config

    @property
    def paused(self):
        return self.main_app.paused

    @paused.setter
    def paused(self, value: bool):
        self.main_app.paused = value

    @property
    def running(self) -> bool:
        return self.main_app.running

    @running.setter
    def running(self, value: bool):
        self.main_app.running = value

    @property
    def quality(self) -> int:
        return self.main_app.quality

    @quality.setter
    def quality(self, value: int):
        self.main_app.quality = value

    @property
    def user(self) -> int:
        return self.main_app.user

    @user.setter
    def user(self, value: int):
        self.main_app.user = value

    @property
    def tile(self) -> Tile:
        return self.main_app.tile

    @tile.setter
    def tile(self, value: Tile):
        self.main_app.tile = value

    @property
    def tile_ref(self) -> Tile:
        return self.main_app.tile_ref

    @tile_ref.setter
    def tile_ref(self, value: Tile):
        self.main_app.tile_ref = value

    @property
    def chunk(self) -> int:
        return self.main_app.chunk

    @chunk.setter
    def chunk(self, value: int):
        self.main_app.chunk = value


class MetricsIf:
    main_app: Main

    @property
    def frame_time(self) -> float:
        return self.main_app.frame_time

    @frame_time.setter
    def frame_time(self, value: float):
        self.main_app.frame_time = value

    @property
    def dectime(self) -> float:
        return self.main_app.dectime

    @dectime.setter
    def dectime(self, value: float):
        self.main_app.dectime = value

    @property
    def viewport_ssim_value(self):
        return self.main_app.viewport_ssim_value

    @viewport_ssim_value.setter
    def viewport_ssim_value(self, value):
        self.main_app.viewport_ssim_value = value

    @property
    def viewport_mse_value(self):
        return self.main_app.viewport_mse_value

    @viewport_mse_value.setter
    def viewport_mse_value(self, value):
        self.main_app.viewport_mse_value = value

    @property
    def proj_ssim_value(self):
        return self.main_app.proj_ssim_value

    @proj_ssim_value.setter
    def proj_ssim_value(self, value):
        self.main_app.proj_ssim_value = value

    @property
    def proj_mse_value(self):
        return self.main_app.proj_mse_value

    @proj_mse_value.setter
    def proj_mse_value(self, value):
        self.main_app.proj_mse_value = value


class ConfigIf:
    main_app: Main

    @property
    def config(self):
        return self.main_app.config

    @config.setter
    def config(self, value: Config):
        self.main_app.config = value

    @property
    def video(self) -> str:
        return self.config.video

    @property
    def projection(self) -> str:
        return self.config.projection

    @property
    def tiling(self) -> str:
        return self.config.tiling

    @property
    def proj_type(self):
        return self.config.proj_type

    @property
    def proj_obj(self) -> ProjectionBase:
        return self.main_app.proj_obj

    @proj_obj.setter
    def proj_obj(self, value: ProjectionBase):
        self.main_app.proj_obj = value

    @property
    def viewport_obj(self) -> Viewport:
        return self.main_app.viewport_obj

    @viewport_obj.setter
    def viewport_obj(self, value: Viewport):
        self.main_app.viewport_obj = value


class ComboIf:
    main_app: Main

    # combo_dict
    @property
    def combo_dict(self):
        return self.main_app.combo_dict

    @combo_dict.setter
    def combo_dict(self, value: dict):
        self.main_app.combo_dict = value

    @property
    def video_name_string_var(self):
        return self.main_app.video_name_string_var

    @video_name_string_var.setter
    def video_name_string_var(self, value: StringVar):
        self.main_app.video_name_string_var = value

    @property
    def projection_string_var(self):
        return self.main_app.projection_string_var

    @projection_string_var.setter
    def projection_string_var(self, value: StringVar):
        self.main_app.projection_string_var = value

    @property
    def tiling_string_var(self):
        return self.main_app.tiling_string_var

    @tiling_string_var.setter
    def tiling_string_var(self, value: StringVar):
        self.main_app.tiling_string_var = value


class PlayerIf:
    main_app: Main

    # video_player
    @property
    def video_player(self):
        return self.main_app.video_player

    @property
    def projection_label(self):
        return self.main_app.projection_label

    @projection_label.setter
    def projection_label(self, value):
        self.main_app.projection_label = value

    @property
    def viewport_label(self):
        return self.main_app.viewport_label

    @viewport_label.setter
    def viewport_label(self, value):
        self.main_app.viewport_label = value


class MainAppIf(StateIf, MetricsIf, ConfigIf, ComboIf, PlayerIf):
    main_app: Main

    # main_app
    @property
    def app_root(self):
        return self.main_app.app_root

    def __init__(self, main_app: Main):
        self.main_app = main_app

    @property
    def user_movement(self):
        return self.config.head_movement_data.loc[(self.video, self.user)]

    @property
    def chunk_path(self) -> Path:
        kwargs = dict(video=self.video, projection=self.projection,
                      tiling=self.tiling, quality=self.quality,
                      tile=self.tile, chunk=self.chunk)
        return Path(self.config.segment_template.format(**kwargs))
