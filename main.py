import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, Tk, Menu
from typing import Optional, Callable, Any

# Para reprodução de vídeo, você precisará do OpenCV e Pillow
# Instale com: pip install opencv-python pillow
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy import ndarray, dtype, floating


class CreateMethods:
    root: Tk
    _open_video_file: Callable
    make_twin_plot: Callable
    update_graph_canvas: Callable
    # _on_slider_change: Callable[[], None]
    # _on_right_side_container_resize: Callable[[], None]
    # graph_frame: ttk.Frame
    # video_full_frame: ttk.LabelFrame
    # video_tile_frame: ttk.LabelFrame
    # video_full_label: ttk.Label
    # video_tile_label: ttk.Label
    # tile_size_slider: ttk.Scale
    # botao_play: ttk.Button

    def _create_menu(self):
        """Cria a barra de menu superior."""
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Open...", command=self._open_video_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

    def _create_graph_area(self):
        """Cria a área de plotagem do Matplotlib à esquerda."""
        self.graph_frame = ttk.Frame(self.root)
        # O gráfico ocupará a linha 0 da coluna 0
        self.graph_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.graph_frame.grid_rowconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(0, weight=1)

        x: ndarray = np.linspace(0, 10, 100)
        y1 = np.sin(x) * 1000 + 1500  # Exemplo de Taxa de Bits (kbps)
        y2 = np.cos(x) ** 2 * 30 + 5  # Exemplo de MSE

        fig = self.make_twin_plot(x, y1, y2,
                                  xlabel="Tempo (s)",
                                  ylabel1="Taxa de Bits (kbps)",
                                  ylabel2="MSE",
                                  suptitle="Métricas de Qualidade do Vídeo")
        self.update_graph_canvas(fig)

    def _create_video_players_area(self):
        """Cria os dois players de vídeo à direita."""
        # Contêiner para os players de vídeo e o slider
        self.right_side_container = ttk.Frame(self.root)
        self.right_side_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Configura as linhas dentro do contêiner da direita
        # Agora, as linhas dos vídeos não se expandem verticalmente (weight=0)
        self.right_side_container.grid_rowconfigure(0, weight=0)  # Vídeo Completo (altura fixa)
        self.right_side_container.grid_rowconfigure(1, weight=0)  # Tile do Vídeo (altura fixa)
        self.right_side_container.grid_rowconfigure(2, weight=0)  # Slider (não se expande)
        self.right_side_container.grid_columnconfigure(0, weight=1)  # Coluna única, ainda se expande horizontalmente

        # --- Player de Vídeo Completo ---
        self.video_full_frame = ttk.LabelFrame(self.right_side_container, text="Vídeo Completo")
        # Define uma altura fixa para o LabelFrame do vídeo completo
        self.video_full_frame.config(height=190)  # Exemplo de altura fixa em pixels
        self.video_full_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 5))
        self.video_full_frame.grid_propagate(False)  # Impede que o LabelFrame redimensione para o conteúdo
        self.video_full_frame.grid_rowconfigure(0, weight=1)  # O Label interno ainda se expande para preencher o frame
        self.video_full_frame.grid_columnconfigure(0, weight=1)

        self.video_full_label = ttk.Label(self.video_full_frame, background="black")
        self.video_full_label.grid(row=0, column=0, sticky="nsew")

        # --- Player de Tile de Vídeo ---
        self.video_tile_frame = ttk.LabelFrame(self.right_side_container, text="Tile do Vídeo")
        # Define uma altura fixa para o LabelFrame do tile de vídeo
        self.video_tile_frame.config(height=190)  # Exemplo de altura fixa em pixels
        self.video_tile_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=5)
        self.video_tile_frame.grid_propagate(False)  # Impede que o LabelFrame redimensione para o conteúdo
        self.video_tile_frame.grid_rowconfigure(0, weight=1)  # O Label interno ainda se expande para preencher o frame
        self.video_tile_frame.grid_columnconfigure(0, weight=1)

        self.video_tile_label = ttk.Label(self.video_tile_frame, background="black")
        self.video_tile_label.grid(row=0, column=0, sticky="nsew")

    def _create_viewport_controls(self):
        """Cria o controle deslizante para o tamanho do tile."""
        # O slider agora está dentro do right_side_container
        slider_frame = ttk.LabelFrame(self.right_side_container, text="Tamanho do Tile")
        slider_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(5, 0))
        slider_frame.grid_columnconfigure(0, weight=1)

        self.botao_play = ttk.Button(slider_frame, text="\u23F8", command=self.play_pause)
        self.botao_play.grid(row=0, column=1, padx=5)
        ttk.Button(slider_frame, text="\u23F9", command=self.parar).grid(row=0, column=2, padx=5)
        ttk.Button(slider_frame, text="Rewind", command=self.rewind).grid(row=0, column=3, padx=5)
        ttk.Checkbutton(slider_frame, text="Repetir", variable=self.repetir).grid(row=0, column=4, padx=5)

        # self.tile_size_slider = ttk.Scale(slider_frame, from_=10, to=100, orient="horizontal", command=self._on_slider_change)
        # self.tile_size_slider.set(50)  # Valor inicial
        # self.tile_size_slider.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    def _create_settings_checkboxes(self):
        """Cria as caixas de seleção na parte inferior."""
        self.settings_frame = ttk.Labelframe(self.root, text="Config")
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


class VideoAnalysisApp(CreateMethods):
    """
    Uma aplicação de GUI para análise de vídeo com gráficos e players.
    """

    def __init__(self, root):
        self.graph_canvas = None
        self.root = root
        self.root.title("Analisador de Vídeo e Gráficos")
        self.root.geometry("1200x800")
        self.repetir = tk.BooleanVar()

        # --- Configuração do Layout Principal ---
        # A grade principal terá 2 colunas e 3 linhas
        # A coluna 0 (gráficos) será mais larga que a coluna 1 (vídeos e controles)
        self.root.grid_columnconfigure(0, weight=1)  # Coluna do gráfico
        self.root.grid_columnconfigure(1, weight=1)  # Coluna dos vídeos/controles

        # As linhas da raiz:
        # Linha 0: Área principal (gráfico à esquerda, vídeos/slider à direita)
        # Linha 1: Checkboxes (inferior)
        self.root.grid_rowconfigure(0, weight=1)  # Linha principal de conteúdo (gráfico e vídeos)
        self.root.grid_rowconfigure(1, weight=0)  # Linha para os checkboxes (não se expande)

        # --- Variáveis de Controle ---
        self.video_path = None
        self.chunk_data_path = None  # Variável para futuros dados de chunk
        self.hm_data_path = None  # Variável para futuros dados de heatmap
        self.video_capture_full: Optional[cv2.VideoCapture] = None
        self.video_capture_tile: Optional[cv2.VideoCapture] = None
        self.checkbox_vars = {}

        # Variáveis para armazenar as dimensões de exibição dos vídeos
        # Inicializadas com valores mínimos, serão atualizadas pelo evento <Configure>
        self.full_video_display_w = 1
        self.full_video_display_h = 1
        self.tile_video_display_w = 1
        self.tile_video_display_h = 1

        # --- Criação dos Widgets ---
        self._create_menu()
        self._create_graph_area()
        self._create_video_players_area()
        self._create_viewport_controls()
        self._create_settings_checkboxes()

        # Vincula o evento <Configure> do contêiner da direita para atualizar as dimensões
        # Isso garante que as dimensões de display sejam sempre as corretas,
        # mesmo após o redimensionamento da janela.
        self.right_side_container.bind('<Configure>', self._on_right_side_container_resize)

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

    def update_graph_canvas(self, fig: plt.Figure):
        # Incorpora o gráfico no Tkinter
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _select_user(self):
        name = self.combo1.get()
        try:
            name_list = self.head_movement.name.unique()
            if name in name_list:
                self.combo6.values = self.head_movement.loc[(name,)].index.unique('users')
        except AttributeError:
            pass

    def _open_video_file(self):
        """Abre um arquivo de vídeo e inicia a reprodução."""
        self.json_path = filedialog.askopenfilename(
            title="Selecione um arquivo de vídeo",
            filetypes=(("Arquivos JSON", "*.json"),
                       ("Todos os arquivos", "*.*"))
        )
        self.json_path = Path(self.json_path)
        meta_data = json.loads(self.json_path.read_text())

        chunk_data_path = 'dataset/' + meta_data['chunk_data']['path']
        head_movement_path = 'dataset/' + meta_data['head_movement']['path']
        tiles_seen_path = 'dataset/' + meta_data['tiles_seen']['path']
        viewport_quality_path = 'dataset/' + meta_data['viewport_quality']['path']

        self.chunk_data = pd.read_hdf(chunk_data_path)
        self.head_movement = pd.read_hdf(head_movement_path)
        self.tiles_seen = pd.read_hdf(tiles_seen_path)
        self.viewport_quality = pd.read_hdf(viewport_quality_path)
        # Define o estado inicial
        # prepara dataset para estatísticas da configuração
        # cria o gráfico no estado inicial
        # reproduz o vídeo sob certa condição
        # condição: nenhum estado deve ser uma estatística
        # criar o dict de paths para 2 chunks (1 de buffer)
        # instanciar o mount_frame (full ou só os vistos)
        # extrair um framde da projeção  # por frame
        # extrair um viewport            # por frame
        self.name = 'cable_cam'
        self.projection = 'cmp'
        self.tiling = '1x1'
        self.quality = 16
        # self.chunk = XX - o chunk não terá um estado inicial pois o gráfico é uma série temporal
        self.user = 0

        def open_video():
            # Libera capturas anteriores se existirem
            if self.video_capture_full and self.video_capture_full.isOpened():
                self.video_capture_full.release()

            # Inicia novas capturas para ambos os players
            self.video_capture_full = cv2.VideoCapture(self.video_path)

            if not self.video_capture_full.isOpened():
                print("Erro ao abrir o arquivo de vídeo.")
                return

            # Força o Tkinter a calcular os tamanhos dos widgets antes de iniciar a reprodução.
            self.root.update_idletasks()
            # Chama a função de redimensionamento para garantir que as dimensões iniciais sejam capturadas
            self._on_right_side_container_resize()

            # Inicia o loop de atualização dos frames
            self.root.after(33, self._update_full_video_frame)
            self.root.after(33, self._update_tile_video_frame)

    def _update_full_video_frame(self):
        """Lê um frame do vídeo completo, converte e exibe."""
        if not self.video_capture_full or not self.video_capture_full.isOpened():
            return

        ret, frame = self.video_capture_full.read()
        if ret:
            # Usa as dimensões de exibição armazenadas nas variáveis de instância
            target_w = self.full_video_display_w
            target_h = self.full_video_display_h

            if target_w > 1 and target_h > 1:  # Garante que as dimensões sejam válidas
                frame_h, frame_w, _ = frame.shape

                if frame_w == 0 or frame_h == 0:
                    self.root.after(33, self._update_full_video_frame)
                    return

                ratio_w = target_w / frame_w
                ratio_h = target_h / frame_h

                ratio = min(ratio_w, ratio_h)

                new_dim = (int(frame_w * ratio), int(frame_h * ratio))
                new_dim = (max(1, new_dim[0]), max(1, new_dim[1]))  # Garante pelo menos 1x1

                frame = cv2.resize(frame, new_dim, interpolation=cv2.INTER_AREA)

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_full_label.imgtk = imgtk
            # noinspection PyTypeChecker
            self.video_full_label.configure(image=imgtk)

        else:
            self.video_capture_full.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self.root.after(33, self._update_full_video_frame)

    # def _update_tile_video_frame(self):
    #     """Lê um frame, recorta o tile e exibe."""
    #     if not self.video_capture_tile or not self.video_capture_tile.isOpened():
    #         return
    #
    #     ret, frame = self.video_capture_tile.read()
    #     if ret:
    #         # Lógica para extrair o tile
    #         h, w, _ = frame.shape
    #         tile_size_percent = self.tile_size_slider.get() / 100.0
    #
    #         tile_w = int(w * tile_size_percent)
    #         tile_h = int(h * tile_size_percent)
    #
    #         tile_w = max(1, tile_w)
    #         tile_h = max(1, tile_h)
    #
    #         start_x = (w - tile_w) // 2
    #         start_y = (h - tile_h) // 2
    #
    #         start_x = max(0, start_x)
    #         start_y = max(0, start_y)
    #
    #         end_x = min(w, start_x + tile_w)
    #         end_y = min(h, start_y + tile_h)
    #
    #         tile_frame = frame[start_y:end_y, start_x:end_x]
    #
    #         # Usa as dimensões de exibição armazenadas nas variáveis de instância
    #         target_w = self.tile_video_display_w
    #         target_h = self.tile_video_display_h
    #
    #         if target_w > 1 and target_h > 1 and tile_frame.size > 0:
    #             frame_h, frame_w, _ = tile_frame.shape
    #             if frame_w == 0 or frame_h == 0:
    #                 self.root.after(33, self._update_tile_video_frame)
    #                 return
    #
    #             ratio_w = target_w / frame_w
    #             ratio_h = target_h / frame_h
    #
    #             ratio = min(ratio_w, ratio_h)
    #
    #             new_dim = (int(frame_w * ratio), int(frame_h * ratio))
    #             new_dim = (max(1, new_dim[0]), max(1, new_dim[1]))  # Garante pelo menos 1x1
    #
    #             if new_dim[0] > 0 and new_dim[1] > 0:
    #                 tile_frame = cv2.resize(tile_frame, new_dim, interpolation=cv2.INTER_AREA)
    #             else:
    #                 self.root.after(33, self._update_tile_video_frame)
    #                 return
    #
    #         cv2image = cv2.cvtColor(tile_frame, cv2.COLOR_BGR2RGB)
    #         img = Image.fromarray(cv2image)
    #         imgtk = ImageTk.PhotoImage(image=img)
    #
    #         self.video_tile_label.imgtk = imgtk
    #         # noinspection PyTypeChecker
    #         self.video_tile_label.configure(image=imgtk)
    #
    #         self.root.after(33, self._update_tile_video_frame)
    #     else:
    #         self.video_capture_tile.set(cv2.CAP_PROP_POS_FRAMES, 0)
    #         self.root.after(33, self._update_tile_video_frame)

    def _on_slider_change(self, value):
        """Chamado quando o valor do slider muda."""
        # A lógica de atualização do tile já lê o valor do slider,
        # então não precisamos fazer nada extra aqui, mas o espaço está reservado.
        pass

    def _on_checkbox_change(self):
        """Chamado quando uma caixa de seleção é marcada/desmarcada."""
        print("--- Estado das Configurações ---")
        for option, var in self.checkbox_vars.items():
            print(f"{option}: {'Ativado' if var.get() else 'Desativado'}")
        print("--------------------------")

    def _on_right_side_container_resize(self, event=None):
        """
        Atualiza as dimensões de exibição dos vídeos quando o contêiner da direita é redimensionado.
        """
        # Força o Tkinter a calcular os tamanhos internos dos widgets
        self.root.update_idletasks()

        # Atualiza as dimensões de exibição usando os tamanhos dos LabelFrames pais
        # Agora, a altura será o valor fixo que definimos
        self.full_video_display_w = self.video_full_frame.winfo_width()
        self.full_video_display_h = self.video_full_frame.winfo_height()
        self.tile_video_display_w = self.video_tile_frame.winfo_width()
        self.tile_video_display_h = self.video_tile_frame.winfo_height()


if __name__ == "__main__":
    app_root = Tk()
    app = VideoAnalysisApp(app_root)
    app_root.mainloop()
