from tkinter import ttk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from lib.main import Main
from lib.interfaces.mainappif import MainAppIf


class Graphs(MainAppIf):
    graphs_frame: ttk.LabelFrame

    tiles_graph_frame: ttk.LabelFrame
    viewport_graph_frame: ttk.LabelFrame

    chunk_fig: plt.Figure
    chunk_ax_bitrate: plt.Axes
    line_bitrate: plt.Line2D

    frame_fig: plt.Figure
    frame_ax_viewport_mse: plt.Axes
    line_viewport_mse: plt.Line2D

    canvas_tiles: FigureCanvasTkAgg
    canvas_viewport: FigureCanvasTkAgg

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self.create_graphs_frame()
        self.create_inner_graphs_frame()
        self.create_graphs()

    def create_graphs_frame(self):
        self.graphs_frame = ttk.LabelFrame(self.app_root, text='Gráficos')
        self.graphs_frame.grid(row=4, column=0, padx=0, pady=0)
        self.graphs_frame.grid_rowconfigure(0, weight=1)
        self.graphs_frame.grid_columnconfigure(0, weight=0)
        self.graphs_frame.grid_columnconfigure(1, weight=0)

    def create_inner_graphs_frame(self):
        # Container para a projeção
        self.tiles_graph_frame = ttk.LabelFrame(self.graphs_frame, text='Gráfico dos tiles')
        self.tiles_graph_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.tiles_graph_frame.grid_rowconfigure(0, weight=1)
        self.tiles_graph_frame.grid_columnconfigure(0, weight=1)

        # Container para o viewport
        self.viewport_graph_frame = ttk.LabelFrame(self.graphs_frame, text='Gráfico do viewport')
        self.viewport_graph_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        self.viewport_graph_frame.grid_rowconfigure(0, weight=1)
        self.viewport_graph_frame.grid_columnconfigure(0, weight=1)

    chunk_x: list[int]
    chunk_y_bitrate: list[int]
    chunk_y_n_tiles: list[int]

    frame_x: list[int]
    frame_y_tiles_mse: list[int]
    frame_y_viewport_mse: list[int]

    chunk_fig: plt.Figure
    frame_fig: plt.Figure

    chunk_ax_bitrate: plt.Axes
    chunk_ax_n_tiles: plt.Axes
    frame_ax_tiles_mse: plt.Axes
    frame_ax_viewport_mse: plt.Axes

    line_bitrate: plt.Line2D
    line_n_tiles: plt.Line2D
    line_tiles_mse: plt.Line2D
    line_viewport_mse: plt.Line2D

    canvas_tiles: FigureCanvasTkAgg
    canvas_viewport: FigureCanvasTkAgg

    def create_graphs(self):
        # left graph
        self.chunk_x = []
        self.chunk_y_bitrate = []
        self.chunk_y_n_tiles = []

        self.chunk_fig, self.chunk_ax_bitrate = plt.subplots(figsize=(4.6, 2.3), dpi=100)
        self.chunk_ax_n_tiles = self.chunk_ax_bitrate.twinx()
        self.chunk_ax_bitrate.set_xlim(0, 60)

        self.line_bitrate, = self.chunk_ax_bitrate.plot([], [], color='tab:blue')
        self.line_n_tiles, = self.chunk_ax_n_tiles.plot([], [], color='tab:olive')

        self.chunk_ax_bitrate.set_xlabel('Chunk')
        self.chunk_ax_bitrate.set_ylabel('Bitrate (Mbps)', color='tab:blue')
        self.chunk_ax_n_tiles.set_ylabel('No. Tiles', color='tab:olive')

        # right graph
        self.frame_x = []
        self.frame_y_tiles_mse = []
        self.frame_y_viewport_mse = []

        self.frame_fig, self.frame_ax_tiles_mse = plt.subplots(figsize=(4.6, 2.3), dpi=100)
        self.frame_ax_viewport_mse = self.frame_ax_tiles_mse.twinx()
        self.frame_ax_tiles_mse.set_xlim(0, 60)

        self.line_viewport_mse, = self.frame_ax_viewport_mse.plot([], [], color='tab:blue')
        self.line_tiles_mse, = self.frame_ax_tiles_mse.plot([], [], color='tab:olive')

        self.frame_ax_tiles_mse.set_xlabel('Chunk')
        self.frame_ax_tiles_mse.set_ylabel('Tiles MSE', color='tab:blue')
        self.frame_ax_viewport_mse.set_ylabel('Viewport MSE', color='tab:olive')

        # figure_canvas
        self.chunk_fig.tight_layout()
        self.frame_fig.tight_layout()
        self.canvas_tiles = FigureCanvasTkAgg(self.chunk_fig, master=self.tiles_graph_frame)
        self.canvas_viewport = FigureCanvasTkAgg(self.frame_fig, master=self.viewport_graph_frame)

        self.canvas_tiles.get_tk_widget().grid(row=0, column=0)
        self.canvas_viewport.get_tk_widget().grid(row=0, column=0)

    def reset(self):
        self.chunk_x.clear()
        self.chunk_y_bitrate.clear()
        self.chunk_y_n_tiles.clear()

        self.line_bitrate.set_data(self.chunk_x, self.chunk_y_bitrate)
        self.line_n_tiles.set_data(self.chunk_x, self.chunk_y_n_tiles)

        self.canvas_tiles.draw()

        self.frame_x.clear()
        self.frame_y_viewport_mse.clear()
        self.frame_x.clear()
        self.frame_y_tiles_mse.clear()

        self.line_viewport_mse.set_data(self.frame_x, self.frame_y_viewport_mse)
        self.line_tiles_mse.set_data(self.frame_x, self.frame_y_tiles_mse)

        self.canvas_viewport.draw()

    def update_graphs_chunk(self, bitrate, n_tiles_seen):
        self.chunk_x.append(self.chunk)

        self.chunk_y_bitrate.append(bitrate)
        self.chunk_y_n_tiles.append(n_tiles_seen)

        self.line_bitrate.set_data(self.chunk_x, self.chunk_y_bitrate)
        self.line_n_tiles.set_data(self.chunk_x, self.chunk_y_n_tiles)

        self.chunk_ax_bitrate.relim()
        self.chunk_ax_bitrate.autoscale_view()

        self.chunk_ax_n_tiles.relim()
        self.chunk_ax_n_tiles.autoscale_view()

        self.canvas_tiles.draw()

    def update_graphs_frame(self, tiles_mse, viewport_mse):
        self.frame_x.append(self.chunk)

        self.frame_y_tiles_mse.append(tiles_mse)
        self.frame_y_viewport_mse.append(viewport_mse)

        self.line_tiles_mse.set_data(self.frame_x, self.frame_y_tiles_mse)
        self.line_viewport_mse.set_data(self.frame_x, self.frame_y_viewport_mse)

        self.frame_ax_tiles_mse.relim()
        self.frame_ax_tiles_mse.autoscale_view()

        self.frame_ax_viewport_mse.relim()
        self.frame_ax_viewport_mse.autoscale_view()

        self.canvas_viewport.draw()
