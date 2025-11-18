from py360tools import Tile

from lib.controlers.config import Config
from lib.controlers.checkboxes import Checkboxes
from lib.controlers.console import Console
from lib.controlers.controls import Controls
from lib.controlers.menu import Menu
from lib.controlers.state import State
from lib.interfaces.mainappbase import MainAppBase


class StateIf(MainAppBase):
    state: State

    @property
    def paused(self):
        return self.state.paused

    @paused.setter
    def paused(self, value: bool):
        self.state.paused = value

    @property
    def running(self) -> bool:
        return self.state.running

    @running.setter
    def running(self, value: bool):
        self.state.running = value

    @property
    def quality(self) -> int:
        return self.state.quality

    @quality.setter
    def quality(self, value: int):
        self.state.quality = value

    @property
    def user(self) -> int:
        return self.state.user

    @user.setter
    def user(self, value: int):
        self.state.user = value

    @property
    def tile(self) -> Tile:
        return self.state.tile

    @tile.setter
    def tile(self, value: Tile):
        self.state.tile = value

    @property
    def tile_ref(self) -> Tile:
        return self.state.tile_ref

    @tile_ref.setter
    def tile_ref(self, value: Tile):
        self.state.tile_ref = value

    @property
    def chunk(self) -> int:
        return self.state.chunk

    @chunk.setter
    def chunk(self, value: int):
        self.state.chunk = value

    @property
    def frame(self) -> int:
        return self.state.frame

    @frame.setter
    def frame(self, value: int):
        self.state.frame = value


class Controllers(MainAppBase):
    @property
    def menu(self) -> Menu:
        return self.main_app.menu

    @property
    def controls(self) -> Controls:
        return self.main_app.controls

    @property
    def checkboxes(self) -> Checkboxes:
        return self.main_app.checkboxes

    @property
    def console(self) -> Console:
        return self.main_app.console

    @property
    def config(self) -> Config:
        return self.main_app.config

    @property
    def state(self) -> State:
        return self.main_app.state


class MainAppIf(Controllers):
    """Interface para a classe Main.
    Ela faz os controladores terem acesso o estado: (nome, projeção, tiling,
    qualidade, tile, chunk, frame, user, ...), e a configuração:

    """

    # main_app
    @property
    def app_root(self):
        return self.main_app.app_root

    # config
    @property
    def user_movement(self):
        return self.config.head_movement_data.loc[(self.state.video, self.state.user)]
