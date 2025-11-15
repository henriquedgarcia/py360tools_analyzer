from collections.abc import Callable

from py360tools import Projection, Tile, Viewport

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


class ConfigIf:
    main_app: Main

    @property
    def config(self):
        return self.main_app.config

    @config.setter
    def config(self, value: Config):
        self.main_app.config = value

    @property
    def frame_time(self) -> float:
        return self.config.frame_time

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
    def proj_obj(self) -> Projection:
        return self.config.proj_obj

    @proj_obj.setter
    def proj_obj(self, value: Projection):
        self.config.proj_obj = value

    @property
    def proj_obj_ref(self) -> Projection:
        return self.config.proj_obj_ref

    @proj_obj_ref.setter
    def proj_obj_ref(self, value: Projection):
        self.config.proj_obj_ref = value

    @property
    def viewport_obj(self) -> Viewport:
        return self.config.viewport_obj

    @viewport_obj.setter
    def viewport_obj(self, value: Viewport):
        self.config.viewport_obj = value

    @property
    def viewport_obj_ref(self) -> Viewport:
        return self.config.viewport_obj_ref

    @viewport_obj_ref.setter
    def viewport_obj_ref(self, value: Viewport):
        self.config.viewport_obj_ref = value


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
    def graphs(self):
        return self.main_app.graphs

    def update_graphs_chunk(self, bitrate, n_tiles) -> Callable:
        return self.graphs.update_graphs_chunk(bitrate, n_tiles)

    def update_graphs_frame(self, tiles_mse, viewport_mse) -> Callable:
        return self.graphs.update_graphs_frame(tiles_mse, viewport_mse)

    def graphs_reset(self) -> Callable:
        return self.graphs.reset()


class ControlsIf:
    main_app: Main

    @property
    def controls(self):
        return self.main_app.controls

    @property
    def button_dict(self):
        return self.controls.button_dict


class PlayerIf:
    main_app: Main

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
    """Interface para a classe Main.
    Ela faz os controladores terem acesso o estado: (nome, projeção, tiling,
    qualidade, tile, chunk, frame, user, ...), e a configuração:

    """
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
