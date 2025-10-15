import json
from functools import cached_property
from pathlib import Path
from tkinter import Tk, ttk, BooleanVar, Label, StringVar, filedialog

import numpy as np
import pandas as pd
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Config:
    config: dict

    video_list: list[str]
    projection_list: list[str]
    tiling_list: list[str]
    quality_list: list[int]

    head_movement_filename: str
    tiles_seen_filename: str
    viewport_quality_filename: str
    chunk_data_filename: str

    def __init__(self, config_file: Path):
        self.config = json.loads(config_file.read_text())
        self.video_list = self.config['video_list']
        self.projection_list = self.config['projection_list']
        self.tiling_list = self.config['tiling_list']
        self.quality_list = self.config['quality_list']

        self.head_movement_filename = self.config['head_movement_filename']
        self.tiles_seen_filename = self.config['tiles_seen_filename']
        self.viewport_quality_filename = self.config['viewport_quality_filename']
        self.chunk_data_filename = self.config['chunk_data_filename']

    @cached_property
    def head_movement_data(self) -> pd.DataFrame:
        return pd.read_hdf(self.head_movement_filename)

    @cached_property
    def tiles_seen_data(self) -> pd.DataFrame:
        return pd.read_hdf(self.tiles_seen_filename)

    @cached_property
    def viewport_quality_data(self) -> pd.DataFrame:
        return pd.read_hdf(self.viewport_quality_filename)

    @cached_property
    def chunk_data(self) -> pd.DataFrame:
        return pd.read_hdf(self.chunk_data_filename)


config: Config


def main():
    """
    A grade principal terá 5 linhas:
    1 - o menu que não é menu: tem dois botões "Abrir paths" e "Abrir HM"
    2 - tem 5 checkboxes:
        - Video ('cable_cam', 'closet_tour','pac_man','sunset')
        - Projeção ('erp', 'cmp')
        - Tiling
        - Qualidade
        - Usuário (depende do vídeo)
    3 - tem dois playes:
        player 1 - Projeção com os ladrilhos selecionados (60% da coluna)
        player 2 - Viewport extraído (40% da coluna)
    4 - tem três botões "reset", "play", "pause" para controlar o vídeo
    5 - Tem dois gráficos:
        esquerda (50% da coluna):
            gráficos gêmeos da série temporal (chunk) de bitrate/dectime dos chunks
        direita (50% da coluna):
            Gráficos gêmeos da série temporal (frame) de mse/ssim do viewport/projeção
    """
    app_root = Tk()
    config_main(app_root)
    create_menu(app_root)
    create_settings_comboboxes(app_root)
    create_players(app_root)
    create_controls(app_root)
    create_graphs(app_root)
    app_root.mainloop()


def config_main(app_root):

    app_root.geometry("1000x720")

    app_root.title('py360tools')

    app_root.grid_columnconfigure(0, weight=1)
    # --- Configuração do Layout Principal ---
    app_root.grid_rowconfigure(0, weight=0)  # menu abrir
    app_root.grid_rowconfigure(1, weight=0)  # Options
    app_root.grid_rowconfigure(2, weight=0)  # players
    app_root.grid_rowconfigure(3, weight=0)  # controle do player
    app_root.grid_rowconfigure(4, weight=1)  # gráficos


def create_menu(app_root):
    nome_arquivo = StringVar(value='Nenhum arquivo selecionado')

    def open_config():
        caminho = filedialog.askopenfilename(title='Selecione um arquivo', initialdir='./',
                                             filetypes=[('application/json', '*.json')])
        json_path = Path(caminho)
        if json_path.suffix != '.json': return
        nome_arquivo.set(json_path.name)  # só o nome do arquivo

        global config
        config = Config(json_path)

        # Atualiza os itens de todos os Combobox, menos user.
        # Atribui valor inicial a todos os combobox, menos user
        # Atualiza Combobox user
        # Atribui valor inicial a user


    menu_frame = ttk.Frame(app_root)
    menu_frame.grid(row=0, column=0, padx=0, pady=5)
    app_root.grid_columnconfigure(0, weight=1)

    open_video_button = ttk.Button(menu_frame, command=open_config, text='Abrir Video Json')
    open_video_button.grid(row=0, column=0, padx=10)

    open_video_label = Label(menu_frame, textvariable=nome_arquivo)
    open_video_label.grid(row=0, column=1, padx=10, sticky='ew')


def create_settings_comboboxes(app_root):
    """Cria as caixas de seleção na parte inferior."""
    settings_frame = ttk.Labelframe(app_root, text='Config')
    settings_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

    combo_dict = {'video': ttk.Combobox(settings_frame, values=[], state='readonly'),
                  'projection': ttk.Combobox(settings_frame, values=[], state='readonly'),
                  'tiling': ttk.Combobox(settings_frame, values=[], state='readonly'),
                  'quality': ttk.Combobox(settings_frame, values=[], state='readonly'),
                  'users': ttk.Combobox(settings_frame, values=[], state='readonly')}

    for idx, (col_name, combo) in enumerate(combo_dict.items()):
        combo.set(col_name)
        combo.grid(row=0, column=idx, padx=5, pady=5, sticky='ew')
        settings_frame.grid_columnconfigure(idx, weight=1)

    def select_user():
        video = combo_dict['video'].get()
        try:
            if video not in config.video_list: raise ValueError
        except ValueError:
            return 'video not found'
        except NameError:
            return 'config not defined'
        dados_filtrados = config.chunk_data.loc[(video,)]
        users_list = list(dados_filtrados.index.unique('users'))
        combo_dict['users'].config(values=users_list)

    combo_dict['users'].configure(postcommand=select_user)


def create_players(app_root: Tk):
    black_img1 = Image.fromarray(np.zeros((230, 460, 3), dtype=np.uint8))
    black_img2 = Image.fromarray(np.zeros((230, 310, 3), dtype=np.uint8))
    black_imgtk1 = ImageTk.PhotoImage(image=black_img1)
    black_imgtk2 = ImageTk.PhotoImage(image=black_img2)

    video_container = ttk.LabelFrame(app_root, text='Videos')
    video_container.grid(row=2, column=0, padx=0, pady=0)
    video_container.grid_rowconfigure(0, weight=1)
    video_container.grid_columnconfigure(0, weight=0)
    video_container.grid_columnconfigure(1, weight=0)

    # Contêiner para o vídeo da projeção
    projection_frame = ttk.LabelFrame(video_container, text='projeção e ladrilhos')
    projection_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
    projection_frame.grid_rowconfigure(0, weight=1)
    projection_frame.grid_columnconfigure(0, weight=1)

    projection_label = Label(projection_frame, image=black_imgtk1, background='magenta')
    projection_label.imgtk = black_imgtk1
    projection_label.grid(row=0, column=0)

    # Contêiner para o viewport
    viewport_frame = ttk.LabelFrame(video_container, text='viewport')
    viewport_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
    viewport_frame.grid_rowconfigure(0, weight=1)
    viewport_frame.grid_columnconfigure(0, weight=1)

    viewport_label = Label(viewport_frame, image=black_imgtk2, background='magenta')
    viewport_label.imgtk = black_imgtk2
    viewport_label.grid(row=0, column=0)


def create_controls(app_root):
    # todo: faltam implementar as funções de controle
    def rewind(): ...

    def stop(): ...

    def play_pause(): ...

    video_control_frame = ttk.LabelFrame(app_root, text='Controles')
    video_control_frame.grid(row=3, column=0, padx=5, pady=5)
    video_control_frame.grid_rowconfigure(0, weight=0)
    for i in range(4):
        video_control_frame.grid_columnconfigure(i, weight=0)

    for column, (text, command) in enumerate(zip(['\u23EE', '\u23F9', '\u25B6'],  #   '\u23F8'
                                                 [rewind, stop, play_pause])):
        button = ttk.Button(video_control_frame, text=text, command=command)
        button.grid(row=0, column=column, padx=5, sticky='ew')

    # botão de repeat
    repeat = BooleanVar()
    repeat_button = ttk.Checkbutton(video_control_frame, text='Repeat',
                                    variable=repeat)
    repeat_button.grid(row=0, column=3, padx=5, sticky='nsew')


def create_graphs(app_root):
    fig, ax = plt.subplots(figsize=(4.6,2.3), dpi=100)
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
    #     app_root.after(100, simular_mse)
    # simular_mse()

    # black_img = Image.fromarray(np.zeros((230, 460, 3), dtype=np.uint8))
    # black_imgtk = ImageTk.PhotoImage(image=black_img)

    graphs_container = ttk.LabelFrame(app_root, text='Gráficos')
    graphs_container.grid(row=4, column=0, padx=0, pady=0)
    graphs_container.grid_rowconfigure(0, weight=1)
    graphs_container.grid_columnconfigure(0, weight=0)
    graphs_container.grid_columnconfigure(1, weight=0)

    tiles_graph_frame = ttk.LabelFrame(graphs_container, text='Gráfico dos tiles')
    tiles_graph_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
    tiles_graph_frame.grid_rowconfigure(0, weight=1)
    tiles_graph_frame.grid_columnconfigure(0, weight=1)

    canvas_widget1 = FigureCanvasTkAgg(fig, master=tiles_graph_frame)
    canvas_widget1.get_tk_widget().grid(row=0, column=0)


    # Contêiner para o viewport
    viewport_graph_frame = ttk.LabelFrame(graphs_container, text='Gráfico do viewport')
    viewport_graph_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
    viewport_graph_frame.grid_rowconfigure(0, weight=1)
    viewport_graph_frame.grid_columnconfigure(0, weight=1)

    canvas_widget2 = FigureCanvasTkAgg(fig, master=viewport_graph_frame)
    canvas_widget2.get_tk_widget().grid(row=0, column=0)


if __name__ == '__main__':
    main()
