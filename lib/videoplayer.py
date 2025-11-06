from pathlib import Path
from tkinter import StringVar, Label, BooleanVar, ttk
from typing import Iterator

import numpy as np
from PIL import Image, ImageTk
from py360tools import Tile

from lib.main import Main
from lib.mainappif import MainAppIf


class VideoPlayer(MainAppIf):
    black_imgtk1: ImageTk.PhotoImage | str
    black_imgtk2: ImageTk.PhotoImage | str
    video_container: ttk.Frame
    projection_frame: ttk.LabelFrame
    viewport_frame: ttk.LabelFrame

    def __init__(self, main_app: 'Main'):
        super().__init__(main_app)
        self._create_default_image()
        self.create_video_container()
        self.create_projection_frame()
        self.create_projection_label()
        self.create_viewport_frame()
        self.create_viewport_label()

    def _create_default_image(self):
        black_img1 = Image.fromarray(np.zeros((230, 460, 3), dtype=np.uint8))
        black_img2 = Image.fromarray(np.zeros((230, 310, 3), dtype=np.uint8))
        self.black_imgtk1: ImageTk.PhotoImage | str = ImageTk.PhotoImage(image=black_img1)
        self.black_imgtk2: ImageTk.PhotoImage | str = ImageTk.PhotoImage(image=black_img2)

    def create_video_container(self):
        """
        Container base para a linha 2. Deve conter dois LabelFrame,
        um para a projeção ladrilhada e outro para o viewport.
        """
        self.video_container = ttk.Frame(self.app_root)
        self.video_container.grid(row=2, column=0, padx=0, pady=0)
        self.video_container.grid_rowconfigure(0, weight=1)
        self.video_container.grid_columnconfigure(0, weight=0)
        self.video_container.grid_columnconfigure(1, weight=0)

    def create_projection_frame(self):
        """
        Um LabelFrame para o vídeo (Label) da projeção com ladrilhos.
        Este container é atualizado a cada frame. São 30 frames por chunk.
        a cada chunk ele abre um novo stream.
        """
        self.projection_frame = ttk.LabelFrame(self.video_container, text='Projeção')
        self.projection_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.projection_frame.grid_rowconfigure(0, weight=1)
        self.projection_frame.grid_columnconfigure(0, weight=1)

    def create_projection_label(self):
        """Um label """
        self.projection_label = Label(self.projection_frame, image=self.black_imgtk1, background='magenta')
        self.projection_label.imgtk = self.black_imgtk1
        self.projection_label.grid(row=0, column=0)

    def create_viewport_frame(self):
        self.viewport_frame = ttk.LabelFrame(self.video_container, text='viewport')
        self.viewport_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        self.viewport_frame.grid_rowconfigure(0, weight=1)
        self.viewport_frame.grid_columnconfigure(0, weight=1)

    def create_viewport_label(self):
        self.viewport_label = Label(self.viewport_frame, image=self.black_imgtk2, background='magenta')
        self.viewport_label.imgtk = self.black_imgtk2
        self.viewport_label.grid(row=0, column=0)

    chunk_hmd_samples_iter: Iterator[tuple[float, float, float]]

    frame_iterator: Iterator[np.ndarray]
    frame_iterator_ref: Iterator[np.ndarray]

    tile_path: dict[str, Path]
    tiles_seen: list[Tile]
    tiles_seen_ref: list[Tile]
    frame_time = float

    pause_icon: StringVar
    play_icon: StringVar
    rewind_icon: StringVar
    stop_icon: StringVar
    repeat: BooleanVar

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
