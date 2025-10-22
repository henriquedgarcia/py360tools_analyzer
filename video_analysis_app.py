import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk, filedialog, Tk, Menu
from typing import Optional, Callable, Union

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class App:
    pass


class Utils:
    ...


@dataclass
class State:
    name: str = None
    projection: str = None
    tiling: str = None
    tile: int = None
    quality: int = None
    chunk: int = None
    frame: int = None


class OpenJsonMethods:
    json_path: Union[str, Path] = None

    def __init__(self, main_app: 'VideoAnalysisApp'):
        self.main_app = main_app
        self.main_window = main_app.main_window
        self._create_menu()

    def _create_menu(self):
        """Cria a barra de menu superior."""
        menu_bar = Menu(self.main_window)
        self.main_window.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_json_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.main_window.quit)

    def open_json_file(self):
        self.json_path = self.show_filedialog()

        (self.chunk_data, self.head_movement,
         self.viewport_quality) = self.load_dataset(self.json_path)

        self.set_initial_state()
        self.update_settings()
        self.plot_graphic()
        self.play_video()

        # OK # Define o estado inicial
        # prepara dataset para estatísticas da configuração
        # cria o gráfico no estado inicial
        # reproduz o vídeo sob certa condição
        # condição: nenhum estado deve ser uma estatística
        # criar o dict de paths para 2 chunks (1 de buffer)
        # instanciar o mount_frame (full ou só os vistos)
        # extrair um framde da projeção  # por frame
        # extrair um viewport            # por frame

    @staticmethod
    def show_filedialog():
        json_path = filedialog.askopenfilename(
            title="Selecione um arquivo de vídeo",
            filetypes=(("Arquivos JSON", "*.json"),
                       ("Todos os arquivos", "*.*"))
            )
        json_path = Path(json_path)

        return json_path

    @staticmethod
    def load_dataset(json_path):
        json_data = json.loads(json_path.read_text())
        chunk_data_path = 'dataset/' + json_data['chunk_data']['path']
        head_movement_path = 'dataset/' + json_data['head_movement']['path']
        viewport_quality_path = 'dataset/' + json_data['viewport_quality']['path']
        chunk_data = pd.read_hdf(chunk_data_path)
        head_movement = pd.read_hdf(head_movement_path)
        viewport_quality = pd.read_hdf(viewport_quality_path)
        return chunk_data, head_movement, viewport_quality

    def set_initial_state(self):
        state = self.main_app.state
        (state.name, state.projection, state.tiling,
         state.tile, state.quality, state.chunk) = self.chunk_data.index[0]
        self.user = self.head_movement.index.unique('user')[0]
        self.frame = self.head_movement.index.unique('frame')[0]

    combo1: ttk.Combobox
    combo2: ttk.Combobox
    combo3: ttk.Combobox
    combo4: ttk.Combobox
    combo5: ttk.Combobox
    combo6: ttk.Combobox

    def update_settings(self):
        self.chunk_data.index.unique('name')
        self.combo1['values'] = self.chunk_data.index.unique('name')
        self.combo2['values'] = self.chunk_data.index.unique('projection')
        self.combo3['values'] = self.chunk_data.index.unique('tiling')
        self.combo4['values'] = self.chunk_data.index.unique('quality')
        self.combo5['values'] = self.chunk_data.index.unique('chunk')
        self.combo6['values'] = self.chunk_data.index.unique('name')

        self.combo1.set('name')
        self.combo2.set('projection')
        self.combo3.set('tiling')
        self.combo4.set('quality')
        self.combo5.set('chunk')
        self.combo6.set('user')

    def play_video(self):
        """
        Inicia a reprodução do vídeo com base no estado atual.
        Precisa ser implementado para carregar o vídeo correto.
        """
        # Exemplo: Construir o caminho do vídeo com base no estado
        # Isso é um placeholder; a lógica real dependerá da estrutura dos seus vídeos
        # e como eles se relacionam com os dados do chunk.

        # Para demonstração, vamos usar um vídeo de exemplo se o nome estiver definido
        if self.main_app.state.name:
            # Assumindo que os vídeos estão em 'dataset/videos/'
            video_name = f"{self.main_app.state.name}.mp4"  # ou .webm, etc.
            video_path = self.json_path.parent / 'dataset' / 'videos' / video_name
            if video_path.exists():
                self.main_app.video_players.open_video(str(video_path))
            else:
                print(f"Vídeo não encontrado: {video_path}")
        else:
            print("Nenhum nome de vídeo definido no estado inicial.")

    def plot_graphic(self):
        x = range(60)
        y1 = np.sin(x)  # Exemplo de Taxa de Bits (kbps)
        fig = self.main_app.graphs.make_serie_plot(x, y1,
                                                   xlabel="Tempo (s)",
                                                   ylabel="Taxa de Bits (kbps)",
                                                   suptitle="Métricas de Qualidade do Vídeo")

        self.main_app.graphs.update_graph_canvas(fig)

    graph_canvas: FigureCanvasTkAgg
    graph_frame: ttk.Frame


class VideoMethods:
    video_capture: Optional[cv2.VideoCapture] = None
    right_side_container: ttk.Frame

    def __init__(self, main_app: 'VideoAnalysisApp'):
        self.main_app = main_app
        self.main_window = main_app.main_window

        self.create_video_area()
        self.create_video_control()

    def create_video_area(self):
        """Cria os dois players de vídeo à direita."""
        # Contêiner para os players de vídeo e o controle
        self.right_side_container = ttk.Frame(self.main_window)

        self.right_side_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Configura as linhas dentro do contêiner da direita
        self.right_side_container.grid_rowconfigure(0, weight=0)  # Vídeo Completo (altura fixa)
        self.right_side_container.grid_rowconfigure(1, weight=0)  # Tile do Vídeo (altura fixa)
        self.right_side_container.grid_rowconfigure(2, weight=0)  # Slider (não se expande)
        self.right_side_container.grid_columnconfigure(0, weight=1)  # Coluna única, ainda se expande horizontalmente
        self.right_side_container.bind('<Configure>', self._on_right_side_container_resize)

        # --- Player de Viewport ---
        self.viewport_frame = ttk.LabelFrame(self.right_side_container, text="Tile do Vídeo")
        self.viewport_frame.config(height=190)  # Exemplo de altura fixa em pixels
        self.viewport_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=5)
        self.viewport_frame.grid_propagate(False)  # Impede que o LabelFrame redimensione para o conteúdo
        self.viewport_frame.grid_rowconfigure(0, weight=1)  # O Label interno ainda se expande para preencher o frame
        self.viewport_frame.grid_columnconfigure(0, weight=1)
        self.video_tile_label = ttk.Label(self.viewport_frame, background="black")
        self.video_tile_label.grid(row=0, column=0, sticky="nsew")

        # --- Player de Vídeo ---
        self.video_frame = ttk.LabelFrame(self.right_side_container, text="Vídeo Completo")
        self.video_frame.config(height=190)  # Exemplo de altura fixa em pixels
        self.video_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 5))
        self.video_frame.grid_propagate(False)  # Impede que o LabelFrame redimensione para o conteúdo
        self.video_frame.grid_rowconfigure(0, weight=1)  # O Label interno ainda se expande para preencher o frame
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_full_label = ttk.Label(self.video_frame, background="black")
        self.video_full_label.grid(row=0, column=0, sticky="nsew")

    def create_video_control(self):
        video_control_frame = ttk.LabelFrame(self.right_side_container, text="Tamanho do Tile")
        video_control_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(5, 0))
        video_control_frame.grid_columnconfigure(0, weight=1)

        self.rewind_button = ttk.Button(video_control_frame, text="\u23EA", command=self.rewind)
        self.stop_button = ttk.Button(video_control_frame, text="\u23F9", command=self.stop)
        self.play_button = ttk.Button(video_control_frame, text="\u23F8", command=self.play_pause)
        self.foward_button = ttk.Button(video_control_frame, text="\u23E9", command=self.foward)

        self.rewind_button.grid(row=0, column=0, padx=0, sticky='ew')
        self.stop_button.grid(row=0, column=1, padx=0)
        self.play_button.grid(row=0, column=2, padx=0)
        self.foward_button.grid(row=0, column=3, padx=0)

        self.repeat = tk.BooleanVar()
        self.repeat_button = ttk.Checkbutton(video_control_frame, text="Repeat", variable=self.repeat)
        self.repeat_button.grid(row=1, column=0, padx=0)

    def open_video(self, video_path):
        # Libera capturas anteriores se existirem
        if self.video_capture and self.video_capture.isOpened():
            self.video_capture.release()

        self.video_capture = cv2.VideoCapture(f'{video_path}')

        if not self.video_capture.isOpened():
            print("Erro ao abrir o arquivo de vídeo.")
            return

        self.main_window.update_idletasks()  # Força o Tkinter a calcular os tamanhos dos widgets antes de iniciar a reprodução.
        self._on_right_side_container_resize()  # Chama a função de redimensionamento para garantir que as dimensões iniciais sejam capturadas

        # Inicia o loop de atualização dos frames
        self.main_window.after(33, self.video_loop)

    def _on_right_side_container_resize(self):
        """
        Atualiza as dimensões de exibição dos vídeos quando o contêiner da direita é redimensionado.
        """
        # Força o Tkinter a calcular os tamanhos internos dos widgets
        self.main_window.update_idletasks()

        # Atualiza as dimensões de exibição usando os tamanhos dos LabelFrames pais
        # Agora, a altura será o valor fixo que definimos
        self.video_display_w = self.video_frame.winfo_width()
        self.video_display_h = self.video_frame.winfo_height()
        self.viewport_display_w = self.viewport_frame.winfo_width()
        self.viewport_display_h = self.viewport_frame.winfo_height()

    def video_loop(self):
        """Lê um frame do vídeo completo, converte e exibe."""
        if self.video_capture and not self.pausado:
            ret, frame = self.video_capture.read()
            if ret:
                frame = cv2.resize(frame, (self.video_display_w, self.video_display_h))
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_full_label.imgtk = imgtk
                self.video_full_label.configure(image=imgtk)
                self.main_window.after(30, self.video_loop)
            else:
                if self.repeat.get():
                    self.rewind()
                    self.video_loop()
                else:
                    self.stop()

    def rewind(self):
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def stop(self):
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
            self.video_full_label.config(image="")
            self.play_button.config(text="Play")

    def foward(self):
        pass

    pausado: bool = False
    play_button: ttk.Button
    exibir_frame: Callable

    def play_pause(self):
        if self.video_capture:
            self.pausado = not self.pausado
            self.play_button.config(text="\u23F8" if not self.pausado else "\u25B6")
            if not self.pausado:
                self.exibir_frame()


class GraphicMethods:
    def __init__(self, main_app):
        self.main_app = main_app
        self.main_window = main_app.main_window

        self._create_graph_area()

    def _create_graph_area(self):
        """Cria a área de plotagem do Matplotlib à esquerda."""
        self.graph_frame = ttk.Frame(self.main_window)
        # O gráfico ocupará a linha 0 da coluna 0
        self.graph_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.graph_frame.grid_rowconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(0, weight=1)

        x = list(range(60))
        y1 = np.sin(x)  # Exemplo de Taxa de Bits (kbps)
        y2 = np.cos(x)  # Exemplo de MSE

        fig = self.make_twin_plot(x, y1, y2,
                                  xlabel="Tempo (s)",
                                  ylabel1="Taxa de Bits (kbps)",
                                  ylabel2="MSE",
                                  suptitle="Métricas de Qualidade do Vídeo")

        self.update_graph_canvas(fig)

    def update_graph_canvas(self, fig: plt.Figure):
        # Incorpora o gráfico no Tkinter
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    @staticmethod
    def make_twin_plot(x, y1, y2, xlabel, ylabel1, ylabel2, suptitle) -> plt.Figure:
        # Dados de exemplo para o gráfico
        fig = plt.figure(figsize=(8, 6), dpi=100)  # Define o tamanho da figura
        ax = fig.add_subplot(111)

        ax.plot(x, y1, label=ylabel1)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel1, color='tab:blue')
        ax.tick_params(axis='y', labelcolor='tab:blue')

        # Eixo Y secundário para MSE
        ax2 = ax.twinx()
        ax2.plot(x, y2, label=ylabel2, color='tab:red', linestyle='--')
        ax2.set_ylabel(ylabel2, color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        fig.suptitle(suptitle)
        fig.tight_layout(rect=(0., 0.03, 1., 0.95))  # Ajusta o layout para evitar sobreposição do título
        return fig

    def make_serie_plot(self, x, y1: dict[str, list[Union[int, float]]], xlabel, ylabel, suptitle) -> plt.Figure:
        """
        Generates a line plot with multiple series using the provided data.

        This method creates a matplotlib figure and uses the given data dictionaries to plot
        multiple line series on the same graph. Each series is labeled in the legend based on
        the keys of the provided data dictionary.

        Parameters:
            x: A sequence containing the x-axis data.
            y1: A dictionary where keys are labels (str) and values are lists of either int or float,
                containing y-axis values for each line series.
            xlabel: Label for the x-axis.
            ylabel: Label for the y-axis.
            suptitle: Title for the entire figure.

        Returns:
            A matplotlib figure containing the generated plot.
        """
        # Dados de exemplo para o gráfico
        fig = plt.figure(figsize=(8, 6), dpi=100)  # Define o tamanho da figura
        ax = fig.add_subplot(111)

        for label, y in y1.items():
            ax.plot(x, y, label=label)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        # ax.tick_params(axis='y', labelcolor='tab:blue')

        fig.suptitle(suptitle)
        fig.tight_layout(rect=(0., 0.03, 1., 0.95))  # Ajusta o layout para evitar sobreposição do título
        return fig

    graph_canvas: FigureCanvasTkAgg


class CreateMethods:
    main_window: Tk

    def __init__(self, main_app: 'VideoAnalysisApp'):
        self.main_app = main_app
        self.main_window = main_app.main_window

        self._create_settings_checkboxes()

    def _create_settings_checkboxes(self):
        """Cria as caixas de seleção na parte inferior."""
        self.settings_frame = ttk.Labelframe(self.main_window, text="Config")
        self.settings_frame.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=10, pady=10)  # Ajustado para row=1 da raiz
        self.combo1 = ttk.Combobox(self.settings_frame, values=[], state="readonly")  # name_list
        self.combo2 = ttk.Combobox(self.settings_frame, values=[], state="readonly")  # proj_list
        self.combo3 = ttk.Combobox(self.settings_frame, values=[], state="readonly")  # tiling
        self.combo4 = ttk.Combobox(self.settings_frame, values=[], state="readonly")  # quality
        self.combo5 = ttk.Combobox(self.settings_frame, values=[], state="readonly")  # chunk
        self.combo6 = ttk.Combobox(self.settings_frame, values=[], state="readonly", postcommand=self._select_user)  # user

        self.combo1.grid(row=0, column=0, padx=5, pady=5)
        self.combo2.grid(row=0, column=1, padx=5, pady=5)
        self.combo3.grid(row=0, column=2, padx=5, pady=5)
        self.combo4.grid(row=0, column=3, padx=5, pady=5)
        self.combo5.grid(row=0, column=4, padx=5, pady=5)
        self.combo6.grid(row=0, column=5, padx=5, pady=5)

        self.combo1.set('name')
        self.combo2.set('projection')
        self.combo3.set('tiling')
        self.combo4.set('quality')
        self.combo5.set('chunk')
        self.combo6.set('user')

    def _select_user(self):
        name = self.combo1.get()
        try:
            name_list = self.main_app.menu.head_movement.name.unique()
            if name in name_list:
                self.combo6.values = self.main_app.menu.head_movement.loc[(name,)].index.unique('users')
        except AttributeError:
            pass


class VideoAnalysisApp(App):
    """
    Uma aplicação de GUI para análise de vídeo com gráficos e players.
    """

    def __init__(self, root):
        self.graph_canvas = None
        self.main_window: tk.Tk = root
        self.main_window.title("Analisador de Vídeo e Gráficos")
        self.main_window.geometry("1200x800")
        self.state = State()

        # --- Configuração do Layout Principal ---
        # A grade principal terá 2 colunas e 3 linhas
        # A coluna 0 (gráficos) será mais larga que a coluna 1 (vídeos e controles)
        # Linha 0: Área principal (gráfico à esquerda, vídeos/slider à direita)
        # Linha 1: Checkboxes (inferior)
        self.main_window.grid_columnconfigure(0, weight=1)  # Coluna do gráfico
        self.main_window.grid_columnconfigure(1, weight=1)  # Coluna dos vídeos/controles
        self.main_window.grid_rowconfigure(0, weight=1)  # Linha principal de conteúdo (gráfico e vídeos)
        self.main_window.grid_rowconfigure(1, weight=0)  # Linha para os checkboxes (não se expande)

        # --- Variáveis de Controle ---
        self.video_path = ''
        self.chunk_data_path = ''  # Variável para futuros dados de chunk
        self.hm_data_path = None  # Variável para futuros dados de heatmap
        self.video_capture_full: Optional[cv2.VideoCapture] = None
        self.checkbox_vars = {}

        # Variáveis para armazenar as dimensões de exibição dos vídeos
        # Inicializadas com valores mínimos, serão atualizadas pelo evento <Configure>
        self.full_video_display_w = 1
        self.full_video_display_h = 1
        self.tile_video_display_w = 1
        self.tile_video_display_h = 1

        # --- Criação dos Widgets ---
        self.menu = OpenJsonMethods(self)
        self.video_players = VideoMethods(self)
        self.graphs = GraphicMethods(self)
        self.comboboxes = CreateMethods(self)


if __name__ == "__main__":
    app_root = Tk()
    app = VideoAnalysisApp(app_root)
    app_root.mainloop()
