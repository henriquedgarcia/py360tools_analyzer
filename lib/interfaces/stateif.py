from py360tools import Tile

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
