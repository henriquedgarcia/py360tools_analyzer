from tkinter import Label, StringVar, Tk, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from py360tools import ProjectionBase, Tile, Viewport

from lib.config import Config


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


class Main:
    graphs_container: ttk.LabelFrame
    tiles_graph_frame: ttk.LabelFrame
    viewport_graph_frame: ttk.LabelFrame
    canvas_widget1: FigureCanvasTkAgg
    canvas_widget2: FigureCanvasTkAgg

    # py360tools
    proj_obj: ProjectionBase
    viewport_obj: Viewport

    # State
    running: bool = False
    paused: bool = True
    video: str
    projection: str
    tiling: str
    quality: int
    user: int
    chunk: int
    tile: Tile
    tile_ref: Tile

    # MetricsIf
    frame_time: float
    dectime: float
    viewport_ssim_value: float
    viewport_mse_value: float
    proj_ssim_value: float
    proj_mse_value: float

    # comboboxes
    combo_dict: dict
    video_name_string_var: StringVar
    projection_string_var: StringVar
    tiling_string_var: StringVar

    # video_player
    viewport_label: Label
    projection_label: Label
    app_root: Tk
    config: Config

    def __init__(self):
        from lib.menu import Menu
        from lib.comboboxes import Comboboxes
        from lib.videoplayer import VideoPlayer
        from lib.controls import Controls

        self.config_main()
        self.menu = Menu(self)
        self.comboboxes = Comboboxes(self)
        self.video_player = VideoPlayer(self)
        self.controls = Controls(self)
        self.create_graphs()
        self.app_root.mainloop()

    def config_main(self):
        self.app_root = Tk()
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

    graphs_container: ttk.LabelFrame
    tiles_graph_frame: ttk.LabelFrame

    canvas_widget1: FigureCanvasTkAgg
    canvas_widget2: FigureCanvasTkAgg
    viewport_graph_frame: ttk.LabelFrame


if __name__ == '__main__':
    Main()
