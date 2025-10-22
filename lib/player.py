from collections.abc import Iterator
from pathlib import Path
from time import time_ns
from tkinter import Tk, ttk, BooleanVar, Label, StringVar, filedialog
from typing import Literal

import numpy as np
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from py360tools import CMP, Viewport, ERP, TileStitcher, ProjectionBase, Tile
from skimage.metrics import mean_squared_error as mse
from skimage.metrics import structural_similarity as ssim

from lib.config import Config

CONTROLS = Literal['play_pause', 'rewind', 'stop', 'repeat']

# """
# import tkinter as tk
# from tkinter import filedialog, ttk
# import json
# import cv2
# from PIL import Image, ImageTk
#
# class VideoPlayer:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Player de Vídeos em Sequência")
#
#         # Interface
#         self.canvas = tk.Label(root)
#         self.canvas.pack()
#
#         self.btn_frame = tk.Frame(root)
#         self.btn_frame.pack()
#
#         self.btn_open = tk.Button(self.btn_frame, text="Abrir", command=self.abrir_json)
#         self.btn_open.pack(side=tk.LEFT)
#
#         self.btn_play = tk.Button(self.btn_frame, text="Play", command=self.play)
#         self.btn_play.pack(side=tk.LEFT)
#
#         self.btn_rewind = tk.Button(self.btn_frame, text="Rewind", command=self.rewind)
#         self.btn_rewind.pack(side=tk.LEFT)
#
#         self.btn_stop = tk.Button(self.btn_frame, text="Stop", command=self.stop)
#         self.btn_stop.pack(side=tk.LEFT)
#
#         # Estado
#         self.video_paths = []
#         self.current_index = 0
#         self.cap = None
#         self.running = False
#
#     def abrir_json(self):
#         file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
#         if file_path:
#             with open(file_path, "r") as f:
#                 self.video_paths = json.load(f)
#             self.current_index = 0
#
#     def play(self):
#         if not self.video_paths:
#             return
#         self.running = True
#         self.cap = cv2.VideoCapture(self.video_paths[self.current_index])
#         self.update_frame()
#
#     def update_frame(self):
#         if not self.running or not self.cap:
#             return
#
#         ret, frame = self.cap.read()
#         if ret:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(frame)
#             imgtk = ImageTk.PhotoImage(image=img)
#             self.canvas.imgtk = imgtk
#             self.canvas.configure(image=imgtk)
#             self.root.after(30, self.update_frame)
#         else:
#             self.cap.release()
#             self.current_index += 1
#             if self.current_index < len(self.video_paths):
#                 self.cap = cv2.VideoCapture(self.video_paths[self.current_index])
#                 self.update_frame()
#             else:
#                 self.running = False
#
#     def rewind(self):
#         self.stop()
#         self.current_index = 0
#         self.play()
#
#     def stop(self):
#         self.running = False
#         if self.cap:
#             self.cap.release()
#         self.canvas.configure(image='')
#
# # Executar
# root = tk.Tk()
# player = VideoPlayer(root)
# root.mainloop()
# """

# segunda versão do copilot com pause
# class VideoPlayer:
#     def __init__(self, root):
#         # ... (interface e botões como antes)
# 
#         self.video_paths = []
#         self.current_index = 0
#         self.cap = None
#         self.running = False
#         self.paused = False
# 
#     def play(self):
#         if not self.video_paths:
#             return
# 
#         # Se já está rodando e não está pausado → pausa
#         if self.running and not self.paused:
#             self.paused = True
#             return
# 
#         # Se está pausado → retoma
#         if self.running and self.paused:
#             self.paused = False
#             self.update_frame()
#             return
# 
#         # Se não está rodando → inicia
#         self.running = True
#         self.paused = False
#         self.cap = cv2.VideoCapture(self.video_paths[self.current_index])
#         self.update_frame()
# 
#     def update_frame(self):
#         if not self.running or self.paused or not self.cap:
#             return
# 
#         ret, frame = self.cap.read()
#         if ret:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(frame)
#             imgtk = ImageTk.PhotoImage(image=img)
#             self.canvas.imgtk = imgtk
#             self.canvas.configure(image=imgtk)
#             self.root.after(30, self.update_frame)
#         else:
#             self.cap.release()
#             self.current_index += 1
#             if self.current_index < len(self.video_paths):
#                 self.cap = cv2.VideoCapture(self.video_paths[self.current_index])
#                 self.update_frame()
#             else:
#                 self.running = False
# 
#     def rewind(self):
#         self.stop()
#         self.current_index = 0
#         self.play()
# 
#     def stop(self):
#         self.running = False
#         self.paused = False
#         if self.cap:
#             self.cap.release()
#         self.canvas.configure(image='')

PAUSE_ICON = StringVar("\u23F8")
PLAY_ICON = StringVar("\u25B6")


class VideoPlayer:
    config: Config = None
    app_root: Tk
    combo_dict: dict[str, ttk.Combobox]
    button_dict: dict[Literal['play_pause', 'rewind', 'stop', 'repeat'], ttk.Button | ttk.Checkbutton]

    video: str
    projection: str
    tiling: str
    quality: int
    user: int
    tile: Tile
    tile_ref: Tile
    chunk: int

    running: bool = False
    paused: bool = True
    current_chunk: int
    chunk_hmd_samples_iter: Iterator[tuple[float, float, float]]
    frame_iterator: Iterator[np.ndarray]
    frame_iterator_ref: Iterator[np.ndarray]
    proj_obj: ProjectionBase
    viewport_obj: Viewport
    tile_path: dict[str, Path]
    tiles_seen: list[Tile]
    tiles_seen_ref: list[Tile]
    frame_time = float

    def play_pause(self):
        if not self.config:
            return

        if not self.running:
            self.frame_time = 1000 / self.config.fps
            self.running = True
            self.paused = False
            self.chunk = 1
            self.update_play_button(PAUSE_ICON)
            self.play_new_chunk()
            return

        # Para todo novo chunk
        if self.paused:
            self.paused = False
            self.update_play_button(PAUSE_ICON)
            self.video_loop()
        else:
            self.paused = True
            self.update_play_button(PLAY_ICON)

            # Inicializa vídeo
            #     calcula bitrate e n_tiles deste chunk
            ...
            # atualize gráfico 1
            #     taxa de bits, n_tiles, tempo de pre-processamento, tiles MSE, chunk MSE
            ...
            # faz a reprodução deste tilestitcher (loop de vídeo do chunk)
            #     next tilestitcher  (se acabou lançará um StopIteration)
            #     next tilestitcher_ref  (se acabou lançará um StopIteration)
            #     next viewport position
            #     ...
            #     extraia o viewport
            #     extraia o viewport_ref
            #
            #     redimensione frame e viewport
            #     (não corrige cor porque estamos fazendo tudo em p/b
            #
            #     converta para Image
            #     Converta para PhotoImage
            #     atribua ao label do vídeo equivalente
            #
            #     atualize gráfico 2
            #     agende o after para 1/fps segundos

    def play_new_chunk(self):
        start = time_ns()

        self.update_state()
        self.update_proj_obj()
        self.update_viewport_obj()
        self.update_tiles_seen_chunk()
        self.update_tiles_path()
        self.config_tile_stitcher()
        self.update_chunk_graphs()

        # calcula o tempo do pré processamento e desconta ele do agendador de frame.
        # se tiver passado de 33ms (1/fps) executa o looop imediatamente
        total_time = (time_ns() - start) / 1000
        diff = self.frame_time - total_time
        diff = diff if diff > 0 else 0

        self.app_root.after(diff, self.video_loop, )

    def update_state(self):
        self.video = self.combo_dict['video'].get()
        self.projection = self.combo_dict['projection'].get()
        self.tiling = self.combo_dict['tiling'].get()
        self.quality = int(self.combo_dict['quality'].get())
        self.user = int(self.combo_dict['user'].get())

    def update_play_button(self, value: StringVar):
        self.button_dict['play_pause'].config(textvariable=value)

    def update_chunk_graphs(self):
        bitrate = sum(tile.path.stat().st_size for tile in self.tiles_seen)
        n_tiles = len(self.tiles_seen)

    def update_proj_obj(self):
        if self.projection == 'cmp':
            self.proj_obj = CMP(proj_res=self.config.cmp_resolution,
                                tiling=self.tiling)
        else:
            self.proj_obj = ERP(proj_res=self.config.erp_resolution,
                                tiling=self.tiling)

    def update_viewport_obj(self):
        self.viewport_obj = Viewport(resolution=self.config.fov_resolution,
                                     fov=self.config.fov,
                                     projection=self.proj_obj)

    def update_tiles_seen_chunk(self):
        """
        pegamos 30 amostras de movimento de cabeça (30 frames == gop == chunk)
        pegamos os tiles vistos para cada uma das 30 amostra a botamos em um set()
            com isto teremos todos os tiles que foram vistos durante o chunk
        usamos esse set para criar duas listas de tiles vistos:
            uma será usada para os tiles de referência (lossless)
            outra será usda para os tiles degradados (QP variado)
        Criamos um iterador com as amostras de cabeça
        """
        frame_ini = (self.chunk - 1) * 30
        frame_end = (self.chunk - 1) * 30 + 30
        chunk_hmd_samples = self.user_movement[frame_ini:frame_end]

        tiles_seen = set()
        for yaw_pitch_roll in chunk_hmd_samples:
            sees = self.viewport_obj.get_vptiles(yaw_pitch_roll)
            tiles_seen.update(sees)

        self.tiles_seen = list(tiles_seen)
        self.tiles_seen_ref = list(tiles_seen)
        self.chunk_hmd_samples_iter = iter(chunk_hmd_samples)

    def update_tiles_path(self):
        for self.tile, self.tile_ref in zip(self.tiles_seen, self.tiles_seen_ref):
            self.tile.path = self.chunk_path

            q = self.quality
            self.quality = 0
            self.tile_ref.path = self.chunk_path
            self.quality = q

    def config_tile_stitcher(self):
        self.frame_iterator = iter(TileStitcher(tiles_seen=self.tiles_seen,
                                                tiling=self.tiling,
                                                proj_res=self.proj_obj.resolution,
                                                ))
        self.frame_iterator_ref = iter(TileStitcher(tiles_seen=self.tiles_seen_ref,
                                                    tiling=self.tiling,
                                                    proj_res=self.proj_obj.resolution,
                                                    ))

    projection_label: Label
    viewport_label: Label

    repeat: BooleanVar

    def post_chunk(self):
        self.chunk += 1
        if self.chunk > 60:
            self.chunk = 0
            if not self.repeat.get():
                return
        self.app_root.after(0, self.play_new_chunk)

    def video_loop(self):
        if self.running and not self.paused:
            try:
                frame = next(self.frame_iterator)
                yaw_pitch_roll = next(self.chunk_hmd_samples_iter)
                viewport_frame = self.viewport_obj.extract_viewport(frame, yaw_pitch_roll)
            except StopIteration:
                self.post_chunk()
                return

            img = Image.fromarray(frame)
            ratio = 1.5 if self.projection == 'cmp' else 2.
            img = img.resize((int(240 * ratio), 240))
            imgtk = ImageTk.PhotoImage(image=img)
            self.projection_label.imgtk = imgtk
            self.projection_label.configure(image=imgtk)

            img = Image.fromarray(viewport_frame)
            img = img.resize((310, 230))
            imgtk = ImageTk.PhotoImage(image=img)
            self.viewport_label.imgtk = imgtk
            self.viewport_label.configure(image=imgtk)

            frame_ref = next(self.frame_iterator_ref)
            proj_mse_value = mse(frame, frame_ref)
            proj_ssim_value = ssim(frame, frame_ref)

            viewport_frame_ref = self.viewport_obj.extract_viewport(frame_ref, yaw_pitch_roll)
            viewport_mse_value = mse(viewport_frame, viewport_frame_ref)
            viewport_ssim_value = ssim(viewport_frame, viewport_frame_ref)

            img = Image.fromarray(viewport_frame)
            img = img.resize(self.proj_obj.shape[::-1])
            imgtk = ImageTk.PhotoImage(image=img)
            self.viewport_label.imgtk = imgtk
            self.viewport_label.configure(image=imgtk)
            # Converta para PhotoImage
            # atribua ao label do vídeo
            # agende o after para 1/fps segundos
            self.app_root.after(self.frame_time, self.video_loop)

    # def video_loop(self):
    #     """Lê um frame do vídeo completo, converte e exibe."""
    #     if self.video_capture and not self.pausado:
    #         ret, frame = self.video_capture.read()
    #         if ret:
    #             frame = cv2.resize(frame, (self.video_display_w, self.video_display_h))
    #             cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #             img = Image.fromarray(cv2image)
    #             imgtk = ImageTk.PhotoImage(image=img)
    #             self.video_full_label.imgtk = imgtk
    #             self.video_full_label.configure(image=imgtk)
    #             self.app_root.after(30, self.video_loop)
    #         else:
    #             if self.repeat.get():
    #                 self.rewind()
    #                 self.video_loop()
    #             else:
    #                 self.stop()
    #
    # def rewind(self):
    #     # todo: converter video_capture em tilestitcher
    #     self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
    #
    # def stop(self):
    #     if self.video_capture:
    #         self.video_capture.release()
    #         self.video_capture = None
    #         self.video_full_label.config(image="")
    #         self.play_button.config(text="Play")

    @property
    def user_movement(self):
        return self.config.head_movement_data.loc[(self.video, self.user)]

    @property
    def chunk_path(self) -> Path:
        kwargs = dict(video=self.video, projection=self.projection,
                      tiling=self.tiling, quality=self.quality,
                      tile=self.tile, chunk=self.chunk)
        return Path(self.config.chunk_data_filename.format(**kwargs))


class MetodosAcessorios(VideoPlayer):
    combo_dict: dict[str, ttk.Combobox]
    nome_arquivo: StringVar

    def update_combobox(self):
        self.combo_dict['video'].config(values=self.config.video_list)
        self.combo_dict['video'].set(self.config.video_list[0])

        self.combo_dict['projection'].config(values=self.config.projection_list)
        self.combo_dict['projection'].set(self.config.projection_list[0])

        self.combo_dict['tiling'].config(values=self.config.tiling_list)
        self.combo_dict['tiling'].set(self.config.tiling_list[0])

        self.combo_dict['quality'].config(values=self.config.quality_list)
        self.combo_dict['quality'].set(self.config.quality_list[0])

    def update_user_combobox(self, event):
        video = self.combo_dict['video'].get()
        dados_filtrados = self.config.head_movement_data.loc[(video, 'cmp')]
        users_list = list(dados_filtrados.index.unique('user'))
        self.combo_dict['user'].config(values=users_list)
        self.combo_dict['user'].set(users_list[0])

    def open_config(self):
        caminho = filedialog.askopenfilename(title='Selecione um arquivo', initialdir='./',
                                             filetypes=[('application/json', '*.json')])
        json_path = Path(caminho)
        if json_path.suffix != '.json': return
        self.nome_arquivo.set(str(json_path))  # só o nome do arquivo
        self.config = Config(json_path)

        self.update_combobox()
        self.init_player()

    def init_player(self):
        ...


class Main(MetodosAcessorios):
    def __init__(self):
        self.app_root = Tk()
        self.config_main()
        self.create_menu()
        self.create_settings_comboboxes()
        self.create_players()
        self.create_controls()
        self.create_graphs()
        self.app_root.mainloop()

    def config_main(self):
        self.app_root.geometry("1000x720")

        self.app_root.title('py360tools')

        self.app_root.grid_columnconfigure(0, weight=1)
        # --- Configuração do Layout Principal ---
        self.app_root.grid_rowconfigure(0, weight=0)  # menu abrir
        self.app_root.grid_rowconfigure(1, weight=0)  # Options
        self.app_root.grid_rowconfigure(2, weight=0)  # players
        self.app_root.grid_rowconfigure(3, weight=0)  # controle do player
        self.app_root.grid_rowconfigure(4, weight=1)  # gráficos

    open_video_button: ttk.Button
    open_video_label: Label

    def create_menu(self):
        menu_frame = ttk.Frame(self.app_root)
        menu_frame.grid(row=0, column=0, padx=0, pady=5)

        self.open_video_button = ttk.Button(menu_frame, command=self.open_config, text='Abrir Video Json')
        self.open_video_button.grid(row=0, column=0, padx=10)

        self.nome_arquivo = StringVar(value='Nenhum arquivo selecionado')
        self.open_video_label = Label(menu_frame, textvariable=self.nome_arquivo)
        self.open_video_label.grid(row=0, column=1, padx=10, sticky='ew')

    def create_settings_comboboxes(self):
        """Cria as caixas de seleção na parte inferior."""
        settings_frame = ttk.Frame(self.app_root)
        settings_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        video_frame = ttk.Labelframe(settings_frame, text='Video')
        video_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        projection_frame = ttk.Labelframe(settings_frame, text='Projeção')
        projection_frame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        tiling_frame = ttk.Labelframe(settings_frame, text='Tiling')
        tiling_frame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        quality_frame = ttk.Labelframe(settings_frame, text='Qualidade (QP)')
        quality_frame.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        users_frame = ttk.Labelframe(settings_frame, text='Usuário ID')
        users_frame.grid(row=0, column=4, padx=5, pady=5, sticky='ew')

        self.combo_dict = {'video': ttk.Combobox(video_frame, values=[], state='readonly'),
                           'projection': ttk.Combobox(projection_frame, values=[], state='readonly'),
                           'tiling': ttk.Combobox(tiling_frame, values=[], state='readonly'),
                           'quality': ttk.Combobox(quality_frame, values=[], state='readonly'),
                           'user': ttk.Combobox(users_frame, values=[], state='readonly')}

        for idx, (col_name, combo) in enumerate(self.combo_dict.items()):
            combo.set(col_name)
            combo.grid(row=0, column=idx, padx=5, pady=5, sticky='ew')
            settings_frame.grid_columnconfigure(idx, weight=1)

        self.combo_dict['video'].bind("<<ComboboxSelected>>", self.update_user_combobox)

    def create_players(self):
        black_img1 = Image.fromarray(np.zeros((230, 460, 3), dtype=np.uint8))
        black_img2 = Image.fromarray(np.zeros((230, 310, 3), dtype=np.uint8))
        self.black_imgtk1: ImageTk.PhotoImage | str = ImageTk.PhotoImage(image=black_img1)
        self.black_imgtk2: ImageTk.PhotoImage | str = ImageTk.PhotoImage(image=black_img2)

        video_container = ttk.Frame(self.app_root)
        video_container.grid(row=2, column=0, padx=0, pady=0)
        video_container.grid_rowconfigure(0, weight=1)
        video_container.grid_columnconfigure(0, weight=0)
        video_container.grid_columnconfigure(1, weight=0)

        # Container para o vídeo da projeção
        projection_frame = ttk.LabelFrame(video_container, text='Projeção')
        projection_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        projection_frame.grid_rowconfigure(0, weight=1)
        projection_frame.grid_columnconfigure(0, weight=1)

        self.projection_label = Label(projection_frame, image=self.black_imgtk1, background='magenta')
        self.projection_label.imgtk = self.black_imgtk1
        self.projection_label.grid(row=0, column=0)

        # Container para o viewport
        viewport_frame = ttk.LabelFrame(video_container, text='viewport')
        viewport_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        viewport_frame.grid_rowconfigure(0, weight=1)
        viewport_frame.grid_columnconfigure(0, weight=1)

        self.viewport_label = Label(viewport_frame, image=self.black_imgtk2, background='magenta')
        self.viewport_label.imgtk = self.black_imgtk2
        self.viewport_label.grid(row=0, column=0)

    def create_controls(self):
        video_control_frame = ttk.LabelFrame(self.app_root, text='Controles')
        video_control_frame.grid(row=3, column=0, padx=5, pady=5)
        video_control_frame.grid_rowconfigure(0, weight=0)

        for i in range(4):
            video_control_frame.grid_columnconfigure(i, weight=0)

        self.repeat = BooleanVar(value=False)
        self.button_dict = {'play_pause': ttk.Button(video_control_frame, text='\u25B6', command=self.play_pause),
                            'rewind': ttk.Button(video_control_frame, text='\u23EE', command=self.rewind),
                            'stop': ttk.Button(video_control_frame, text='\u23F9', command=self.stop),
                            'repeat': ttk.Checkbutton(video_control_frame, text='Repeat', variable=self.repeat),
                            }
        for column, button in enumerate(self.button_dict.values()):
            button.grid(row=0, column=column, padx=5, sticky='ew')

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

        graphs_container = ttk.LabelFrame(self.app_root, text='Gráficos')
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

        # Container para o viewport
        viewport_graph_frame = ttk.LabelFrame(graphs_container, text='Gráfico do viewport')
        viewport_graph_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        viewport_graph_frame.grid_rowconfigure(0, weight=1)
        viewport_graph_frame.grid_columnconfigure(0, weight=1)

        canvas_widget2 = FigureCanvasTkAgg(fig, master=viewport_graph_frame)
        canvas_widget2.get_tk_widget().grid(row=0, column=0)


if __name__ == '__main__':
    Main()
