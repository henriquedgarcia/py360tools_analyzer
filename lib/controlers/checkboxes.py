import tkinter as tk
from tkinter import ttk

from lib.main import Main
from lib.interfaces.mainappif import MainAppIf


class Checkboxes(MainAppIf):
    checkbox_var_dict: dict[str, tk.BooleanVar]

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self._create_checkboxes_main_frame()
        self._create_select_buttons()
        self._create_checkboxes()

    def _create_checkboxes_main_frame(self):
        self.checkboxes_main_frame = ttk.Frame(self.app_root)
        self.checkboxes_main_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.select_button_frame = ttk.Frame(self.checkboxes_main_frame)
        self.select_button_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.select_button_frame.grid_columnconfigure(0, weight=1)
        self.select_button_frame.grid_rowconfigure(0, weight=1)
        self.select_button_frame.grid_rowconfigure(1, weight=1)

        self.checkboxes_frame = ttk.Labelframe(self.checkboxes_main_frame, text='Metrics')
        self.checkboxes_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        for idx in range(len(self.metric_list[0])):
            self.checkboxes_frame.grid_columnconfigure(idx, weight=1)
        self.checkboxes_frame.grid_rowconfigure(0, weight=0)
        self.checkboxes_frame.grid_rowconfigure(1, weight=0)

    metric_list = [['avg_viewport_ssim', 'avg_viewport_mse',
                    'avg_tile_mse', 'avg_tile_ssim',
                    'avg_tile_s_mse', 'avg_tile_ws_mse'],
                   ['bitrate', 'tiles_seen_heat_map', 'n_tiles_seen',
                    'velocidade']]

    def _create_select_buttons(self):
        self.button_select_all = ttk.Button(self.select_button_frame, text='Select All')
        self.button_select_all.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.button_select_all.configure(command=self.select_all)

        self.button_select_None = ttk.Button(self.select_button_frame, text='Select None')
        self.button_select_None.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        self.button_select_None.configure(command=self.select_none)

    def select_all(self):
        for value in self.checkbox_var_dict.values():
            value.set(True)

    def select_none(self):
        for value in self.checkbox_var_dict.values():
            value.set(False)

    def _create_checkboxes(self):
        """Cria as caixas de seleção na parte inferior."""
        self.checkbox_var_dict = {}
        for n, metric in enumerate(self.metric_list[0]):
            variable = tk.BooleanVar()
            variable.set(True)
            check_button = tk.Checkbutton(self.checkboxes_frame, text=metric,
                                          variable=variable, offvalue=False,
                                          onvalue=True)
            check_button.grid(row=0, column=n, padx=0, pady=0, sticky='w')
            self.checkbox_var_dict[metric] = variable

        for n, metric in enumerate(self.metric_list[1]):
            variable = tk.BooleanVar()
            variable.set(True)
            check_button = tk.Checkbutton(self.checkboxes_frame, text=metric,
                                          variable=variable, offvalue=False,
                                          onvalue=True)
            check_button.grid(row=1, column=n, padx=0, pady=0, sticky='w')
            self.checkbox_var_dict[metric] = variable
