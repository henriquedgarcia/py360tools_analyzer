from collections.abc import Callable
from pathlib import Path

from matplotlib import pyplot as plt
from py360tools import ProjectionBase, Tile, Viewport

from lib.config import Config
from lib.main import Main


class StateIf:
    main_app: Main

    @property
    def paused(self):
        return self.main_app.state.paused

    @paused.setter
    def paused(self, value: bool):
        self.main_app.state.paused = value

    @property
    def running(self) -> bool:
        return self.main_app.state.running

    @running.setter
    def running(self, value: bool):
        self.main_app.state.running = value

    @property
    def quality(self) -> int:
        return self.main_app.state.quality

    @quality.setter
    def quality(self, value: int):
        self.main_app.state.quality = value

    @property
    def user(self) -> int:
        return self.main_app.state.user

    @user.setter
    def user(self, value: int):
        self.main_app.state.user = value

    @property
    def tile(self) -> Tile:
        return self.main_app.state.tile

    @tile.setter
    def tile(self, value: Tile):
        self.main_app.state.tile = value

    @property
    def tile_ref(self) -> Tile:
        return self.main_app.state.tile_ref

    @tile_ref.setter
    def tile_ref(self, value: Tile):
        self.main_app.state.tile_ref = value

    @property
    def chunk(self) -> int:
        return self.main_app.state.chunk

    @chunk.setter
    def chunk(self, value: int):
        self.main_app.state.chunk = value

    @property
    def frame(self) -> int:
        return self.main_app.state.frame

    @frame.setter
    def frame(self, value: int):
        self.main_app.state.frame = value


class MetricsIf:
    main_app: Main

    @property
    def frame_time(self) -> float:
        return self.main_app.controls.frame_time

    @frame_time.setter
    def frame_time(self, value: float):
        self.main_app.controls.frame_time = value

    @property
    def dectime(self) -> float:
        return self.main_app.controls.dectime

    @dectime.setter
    def dectime(self, value: float):
        self.main_app.controls.dectime = value

    @property
    def viewport_ssim_value(self):
        return self.main_app.controls.viewport_ssim_value

    @viewport_ssim_value.setter
    def viewport_ssim_value(self, value):
        self.main_app.controls.viewport_ssim_value = value

    @property
    def viewport_mse_value(self):
        return self.main_app.controls.viewport_mse_list

    @viewport_mse_value.setter
    def viewport_mse_value(self, value):
        self.main_app.controls.viewport_mse_list = value

    @property
    def proj_ssim_value(self):
        return self.main_app.controls.proj_ssim_value

    @proj_ssim_value.setter
    def proj_ssim_value(self, value):
        self.main_app.controls.proj_ssim_value = value

    @property
    def proj_mse_value(self):
        return self.main_app.controls.proj_mse_list

    @proj_mse_value.setter
    def proj_mse_value(self, value):
        self.main_app.controls.proj_mse_list = value


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
    def proj_obj_ref(self) -> ProjectionBase:
        return self.main_app.proj_obj_ref

    @proj_obj_ref.setter
    def proj_obj_ref(self, value: ProjectionBase):
        self.main_app.proj_obj_ref = value

    @property
    def viewport_obj(self) -> Viewport:
        return self.main_app.viewport_obj

    @viewport_obj.setter
    def viewport_obj(self, value: Viewport):
        self.main_app.viewport_obj = value

    @property
    def viewport_obj_ref(self) -> Viewport:
        return self.main_app.viewport_obj_ref

    @viewport_obj_ref.setter
    def viewport_obj_ref(self, value: Viewport):
        self.main_app.viewport_obj_ref = value


class ComboIf:
    main_app: Main

    # combo_dict
    @property
    def combo_dict(self):
        return self.main_app.comboboxes.combo_dict

    @property
    def video_name_string_var(self):
        return self.main_app.comboboxes.video_name_string_var

    @property
    def projection_string_var(self):
        return self.main_app.comboboxes.projection_string_var

    @property
    def tiling_string_var(self):
        return self.main_app.comboboxes.tiling_string_var


class GraphsIf:
    main_app: Main

    @property
    def update_graphs_chunk(self) -> Callable:
        return self.main_app.graphs.update_graphs_chunk

    @property
    def update_graphs_frame(self) -> Callable:
        return self.main_app.graphs.update_graphs_frame

    @property
    def reset(self) -> Callable:
        return self.main_app.graphs.reset

    # @property
    # def chunk_y_bitrate(self):
    #     return self.main_app.graphs.chunk_y_bitrate
    #
    # @property
    # def chunk_x_n_tiles(self):
    #     return self.main_app.graphs.chunk_x_n_tiles
    #
    # @property
    # def chunk_y_n_tiles(self):
    #     return self.main_app.graphs.chunk_y_n_tiles
    #
    # @property
    # def frame_x_viewport_mse(self):
    #     return self.main_app.graphs.frame_x_viewport_mse
    #
    # @property
    # def frame_y_viewport_mse(self):
    #     return self.main_app.graphs.frame_y_viewport_mse
    #
    # @property
    # def frame_x_tiles_mse(self):
    #     return self.main_app.graphs.frame_x_tiles_mse
    #
    # @property
    # def frame_y_tiles_mse(self):
    #     return self.main_app.graphs.frame_y_tiles_mse
    #
    # @property
    # def line_bitrate(self) -> plt.Line2D:
    #     return self.main_app.graphs.line_bitrate
    #
    # @property
    # def line_n_tiles(self) -> plt.Line2D:
    #     return self.main_app.graphs.line_n_tiles
    #
    # @property
    # def line_viewport_mse(self) -> plt.Line2D:
    #     return self.main_app.graphs.line_viewport_mse
    #
    # @property
    # def line_tiles_mse(self) -> plt.Line2D:
    #     return self.main_app.graphs.line_tiles_mse
    #
    # @property
    # def canvas_tiles(self):
    #     return self.main_app.graphs.canvas_tiles
    #
    # @property
    # def canvas_viewport(self):
    #     return self.main_app.graphs.canvas_viewport
    #
    # @property
    # def chunk_fig(self):
    #     return self.main_app.graphs.chunk_fig
    #
    # @property
    # def frame_fig(self):
    #     return self.main_app.graphs.frame_fig
    #
    # @property
    # def chunk_ax_bitrate(self):
    #     return self.main_app.graphs.chunk_ax_bitrate
    #
    # @property
    # def chunk_ax_n_tiles(self):
    #     return self.main_app.graphs.chunk_ax_bitrate


class PlayerIf:
    main_app: Main

    # video_player
    @property
    def video_player(self):
        return self.main_app.video_player

    @property
    def projection_label(self):
        return self.video_player.projection_label

    @projection_label.setter
    def projection_label(self, value):
        self.video_player.projection_label = value

    @property
    def viewport_label(self):
        return self.video_player.viewport_label

    @viewport_label.setter
    def viewport_label(self, value):
        self.video_player.viewport_label = value


class MainAppIf(StateIf, ConfigIf):
    main_app: Main

    def __init__(self, main_app: Main):
        self.main_app = main_app

    # main_app
    @property
    def app_root(self):
        return self.main_app.app_root

    # config
    @property
    def user_movement(self):
        return self.config.head_movement_data.loc[(self.video, self.user)]

    @property
    def chunk_path(self) -> Path:
        kwargs = dict(video=self.video, projection=self.projection,
                      tiling=self.tiling, quality=self.quality,
                      tile=self.tile, chunk=self.chunk)
        return Path(self.config.segment_template.format(**kwargs))
