from tkinter import ttk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from lib.main import Main
from lib.mainappif import MainAppIf


class Graphs(MainAppIf):
    def __init__(self, main_app: 'Main'):
        super().__init__(main_app)
        self.fig, self.ax = plt.subplots(figsize=(4.6, 2.3), dpi=100)
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlim(0, 1800)
        self.ax.set_ylim(0, 10)
        self.create_graphs()

    def create_graphs(self):
        fig, ax = plt.subplots(figsize=(4.6, 2.3), dpi=100)
        line, = ax.plot([], [], lw=2)
        ax.set_xlim(0, 1800)
        ax.set_ylim(0, 10)

        x_data, y_data = [], []

        # def atualizar_grafico(mse_valor):
        #     x_data.append(len(x_data))
        #     y_data.append(mse_valor)
        #     line.set_data(x_data, y_data)
        #     canvas_widget.draw()

        # def simular_mse():
        #     mse_valor = np.random.rand()
        #     atualizar_grafico(mse_valor)
        #     self.app_root.after(100, simular_mse)
        # simular_mse()

        self.graphs_container = ttk.LabelFrame(self.app_root, text='Gráficos')
        self.graphs_container.grid(row=4, column=0, padx=0, pady=0)
        self.graphs_container.grid_rowconfigure(0, weight=1)
        self.graphs_container.grid_columnconfigure(0, weight=0)
        self.graphs_container.grid_columnconfigure(1, weight=0)

        self.tiles_graph_frame = ttk.LabelFrame(self.graphs_container, text='Gráfico dos tiles')
        self.tiles_graph_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.tiles_graph_frame.grid_rowconfigure(0, weight=1)
        self.tiles_graph_frame.grid_columnconfigure(0, weight=1)

        self.canvas_widget1 = FigureCanvasTkAgg(fig, master=self.tiles_graph_frame)
        self.canvas_widget1.get_tk_widget().grid(row=0, column=0)

        # Container para o viewport
        self.viewport_graph_frame = ttk.LabelFrame(self.graphs_container, text='Gráfico do viewport')
        self.viewport_graph_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        self.viewport_graph_frame.grid_rowconfigure(0, weight=1)
        self.viewport_graph_frame.grid_columnconfigure(0, weight=1)

        self.canvas_widget2 = FigureCanvasTkAgg(fig, master=self.viewport_graph_frame)
        self.canvas_widget2.get_tk_widget().grid(row=0, column=0)
