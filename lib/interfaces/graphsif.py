from typing import Callable

from lib.interfaces.mainappbase import MainAppBase


class GraphsIf(MainAppBase):
    @property
    def graphs(self):
        return self.main_app.post_processing.graphs

    def update_graphs_chunk(self, bitrate, n_tiles) -> Callable:
        return self.graphs.update_graphs_chunk(bitrate, n_tiles)

    def update_graphs_frame(self, tiles_mse, viewport_mse) -> Callable:
        return self.graphs.update_graphs_frame(tiles_mse, viewport_mse)

    def graphs_reset(self) -> Callable:
        return self.graphs.reset()
