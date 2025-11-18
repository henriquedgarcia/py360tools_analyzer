from typing import Optional

from py360tools import Tile


class State:
    running: bool = False
    paused: bool = True
    video: str = None
    projection: str = None
    tiling: str = None
    quality: int = None
    user: int = None
    chunk: int = None
    frame: int = None
    tile: Optional[Tile] = None
    tile_ref: Optional[Tile] = None
