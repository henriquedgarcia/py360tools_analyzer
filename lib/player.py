import json
from functools import cached_property
from pathlib import Path
from tkinter import Tk, ttk, BooleanVar, Label, StringVar, filedialog

import pandas as pd


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
    # create_players(app_root)
    # create_controls(app_root)
    # create_graphs(app_root)
    app_root.mainloop()


def config_main(app_root):
    app_root.title("py360tools")
    app_root.geometry("1200x800")

    # --- Configuração do Layout Principal ---
    app_root.grid_rowconfigure(0, weight=0)  # menu abrir
    app_root.grid_rowconfigure(1, weight=0)  # Options
    app_root.grid_rowconfigure(2, weight=0)  # players
    app_root.grid_rowconfigure(3, weight=0)  # controle do player
    app_root.grid_rowconfigure(4, weight=1)  # gráficos


def create_menu(app_root):
    nome_arquivo = StringVar(value="Nenhum arquivo selecionado")

    def open_config():
        caminho = filedialog.askopenfilename(title="Selecione um arquivo", initialdir='./',
                                             filetypes=[('application/json', '*.json')])
        json_path = Path(caminho)
        if json_path.suffix != '.json': return
        nome_arquivo.set(json_path.name)  # só o nome do arquivo

        global config
        config = Config(json_path)

    menu_frame = ttk.Frame(app_root)
    menu_frame.grid(row=0, column=0, padx=0, pady=5)

    open_video_button = ttk.Button(menu_frame, command=open_config, text="Abrir Video Json")
    open_video_button.grid(row=0, column=0, padx=10)

    open_video_label = Label(menu_frame, textvariable=nome_arquivo)
    open_video_label.grid(row=0, column=1, padx=10, sticky="ew")


def create_settings_comboboxes(app_root):
    """Cria as caixas de seleção na parte inferior."""
    settings_frame = ttk.Labelframe(app_root, text="Config")
    settings_frame.grid(row=1, column=0, padx=0, pady=5)

    combo_list = {'video': ttk.Combobox(settings_frame, values=[], state="readonly"),
                  'projection': ttk.Combobox(settings_frame, values=[], state="readonly"),
                  'tiling': ttk.Combobox(settings_frame, values=[], state="readonly"),
                  'quality': ttk.Combobox(settings_frame, values=[], state="readonly"),
                  'users': ttk.Combobox(settings_frame, values=[], state="readonly")}

    for idx, (col_name, combo) in enumerate(combo_list.items()):
        combo.set(col_name)
        combo.grid(row=0, column=idx, padx=5, pady=5)

    def select_user():
        video = combo_list['video'].get()
        if video not in config.video_list: return
        dados_filtrados = config.chunk_data.loc[(video,)]
        users_list = list(dados_filtrados.index.unique('users'))
        combo_list['users'].config(values=users_list)

    combo_list['users'].configure(postcommand=select_user)


def create_players(app_root):
    # todo: Falta ajustar o frame dos vídeos
    video_container = ttk.Frame(app_root)
    video_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
    video_container.grid_columnconfigure(0, weight=1)  # Coluna única, ainda se expande horizontalmente
    video_container.grid_columnconfigure(1, weight=0)  # Coluna única, ainda se expande horizontalmente

    # video_container.bind('<Configure>', _on_right_side_container_resize)

    """Cria os dois players de vídeo à direita."""
    # Contêiner para os players de vídeo e o controle
    projection_frame = ttk.LabelFrame(video_container, text="projeção e ladrilhos")
    projection_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Configura as linhas dentro do contêiner da direita
    video_container.grid_rowconfigure(0, weight=0)  # Vídeo Completo (altura fixa)
    video_container.grid_rowconfigure(1, weight=0)  # Tile do Vídeo (altura fixa)
    video_container.grid_rowconfigure(2, weight=0)  # Slider (não se expande)
    video_container.grid_columnconfigure(0, weight=1)  # Coluna única, ainda se expande horizontalmente
    # video_container.bind('<Configure>', _on_right_side_container_resize)

    # --- Player de Viewport ---
    viewport_frame = ttk.LabelFrame(app_root, text="Tile do Vídeo")
    viewport_frame.config(height=190)  # Exemplo de altura fixa em pixels
    viewport_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=5)
    viewport_frame.grid_propagate(False)  # Impede que o LabelFrame redimensione para o conteúdo
    viewport_frame.grid_rowconfigure(0, weight=1)  # O Label interno ainda se expande para preencher o frame
    viewport_frame.grid_columnconfigure(0, weight=1)
    video_tile_label = ttk.Label(viewport_frame, background="black")
    video_tile_label.grid(row=0, column=0, sticky="nsew")

    # --- Player de Vídeo ---
    video_frame = ttk.LabelFrame(app_root, text="Vídeo Completo")
    video_frame.config(height=190)  # Exemplo de altura fixa em pixels
    video_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 5))
    video_frame.grid_propagate(False)  # Impede que o LabelFrame redimensione para o conteúdo
    video_frame.grid_rowconfigure(0, weight=1)  # O Label interno ainda se expande para preencher o frame
    video_frame.grid_columnconfigure(0, weight=1)
    video_full_label = ttk.Label(video_frame, background="black")
    video_full_label.grid(row=0, column=0, sticky="nsew")


def create_controls(app_root):
    # todo: faltam implementar as funções de controle
    def rewind(): ...

    def stop(): ...

    def play_pause(): ...

    video_control_frame = ttk.LabelFrame(app_root, text="Tamanho do Tile")
    video_control_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=(5, 0))
    video_control_frame.grid_columnconfigure(0, weight=1)

    for column, (text, command) in enumerate(zip(["\u23EA", "\u23F9", "\u23F8"],
                                                 [rewind, stop, play_pause])):
        button = ttk.Button(video_control_frame, text=text, command=command)
        button.grid(row=0, column=column, padx=0, sticky='ew')

    # botão de repeat
    repeat = BooleanVar(value=True)
    repeat_button = ttk.Checkbutton(video_control_frame, text="Repeat", variable=repeat)
    repeat_button.grid(row=1, column=0, padx=0)


def create_graphs(app_root):
    graphs_frame = ttk.LabelFrame(app_root, text="Gráficos")
    graphs_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(5, 0))
    # todo: Falta tudo


if __name__ == "__main__":
    main()
