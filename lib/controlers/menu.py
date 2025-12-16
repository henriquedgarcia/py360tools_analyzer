import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Union

from lib.interfaces.mainappif import MainAppIf
from lib.main import Main


class Menu(MainAppIf):
    menu_frame: ttk.Frame
    json_path: Union[str, Path]

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self._create_frame()
        self._create_buttons()
        self._create_labels_frame()

    def _create_frame(self):
        self.menu_frame = ttk.Frame(self.app_root)
        self.menu_frame.grid(row=0, column=0, padx=0, pady=5, sticky='nsew')
        self.menu_frame.grid_rowconfigure(0, weight=1)
        self.menu_frame.grid_columnconfigure(0, weight=0)
        self.menu_frame.grid_columnconfigure(1, weight=1)

        self.button_frame = ttk.Frame(self.menu_frame)
        self.button_frame.grid(row=0, column=0, padx=0, pady=0, sticky='sew')
        self.button_frame.grid_rowconfigure(0, weight=1)

        self.label_frame_main = ttk.Frame(self.menu_frame)
        self.label_frame_main.grid(row=0, column=1, padx=0, pady=0, sticky='nsew')
        self.label_frame_main.grid_rowconfigure(0, weight=0)
        for i in range(7):
            self.label_frame_main.grid_rowconfigure(i, weight=1)

    def _create_buttons(self):
        button_list = {'Open': self.controls.open,
                       'Save': self.controls.save,
                       'Start': self.controls.start,
                       'Stop': self.controls.stop,
                       'Clean': self.controls.clean}

        self.button_dict: dict[str, ttk.Button] = {}
        for n, (button, command) in enumerate(button_list.items()):
            self.button_dict[button] = ttk.Button(self.button_frame, text=button,
                                                  command=command)
            self.button_dict[button].grid(row=0, column=n, padx=2, sticky='w')

    string_var_dict: dict[str, tk.StringVar]
    param_list = ['video', 'projection', 'tiling', 'user', 'quality', 'chunk', 'metric']

    def _create_labels_frame(self):
        self.string_var_dict = {}
        for n, param in enumerate(self.param_list):
            self.string_var_dict[param] = tk.StringVar(value='-----')
            label_frame = tk.LabelFrame(self.label_frame_main, text=param)
            label_frame.grid(row=0, column=n, padx=0, pady=0, sticky='nsew')

            label = tk.Label(label_frame, textvariable=self.string_var_dict[param], background='white')
            label.grid(row=0, column=0, padx=5, pady=0, sticky='nsew')

    def update_labels_frame(self, param: str, value: str):
        """
        param = 'video'|'projection'|'tiling'|'user'|'quality'|'chunk'|'metric'

        """
        self.string_var_dict[param].set(value)
