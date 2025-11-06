from json import JSONDecodeError
from pathlib import Path
from tkinter import filedialog, Label, StringVar, ttk
from typing import Union

from py360tools import Viewport

from lib.config import Config
from lib.main import Main
from lib.mainappif import MainAppIf


class Menu(MainAppIf):
    menu_frame: ttk.Frame
    json_path: Union[str, Path]

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self._create_frame()
        self._create_buttons()
        self._create_label()

    def _create_frame(self):
        self.menu_frame = ttk.Frame(self.app_root)
        self.menu_frame.grid(row=0, column=0, padx=0, pady=5)

    def _create_buttons(self):
        self.open_video_button = ttk.Button(self.menu_frame,
                                            command=self.open_config,
                                            text='Abrir Video Json')
        self.open_video_button.grid(row=0, column=0, padx=10)

    def _create_label(self):
        self.json_path_stringvar = StringVar(value='Nenhum arquivo selecionado')
        self.open_video_label = Label(self.menu_frame, textvariable=self.json_path_stringvar)
        self.open_video_label.grid(row=0, column=1, padx=10, sticky='ew')

    def open_config(self):
        self.json_path = filedialog.askopenfilename(title='Selecione um arquivo',
                                                    initialdir='./',
                                                    filetypes=[('application/json',
                                                                '*.json')])
        self.json_path = Path(self.json_path)

        self.load_config()
        self.update_labels()
        self.update_combobox()
        self.update_proj_obj()
        self.update_viewport_obj()
        self.init_player()

    def load_config(self):
        try:
            self.config = Config(self.json_path)
        except JSONDecodeError as e:
            self.json_path_stringvar.set('JSONDecodeError')
            raise e

    def update_labels(self):
        self.json_path_stringvar.set(self.json_path)
        self.video_name_string_var.set(self.config.video)
        self.projection_string_var.set(self.config.projection)
        self.tiling_string_var.set(self.config.tiling)

    def update_combobox(self):
        self.combo_dict['quality'].config(values=self.config.quality_list)
        self.combo_dict['quality'].set(self.config.quality_list[0])
        self.update_user_combobox()

    def update_user_combobox(self):
        users_list = self.get_users_list()
        self.combo_dict['user'].config(values=users_list)
        self.combo_dict['user'].set(users_list[0])

    def get_users_list(self) -> list[int]:
        video = self.config.video
        dados_filtrados = self.config.head_movement_data.loc[(video,)]
        users_list = list(dados_filtrados.index.unique('user'))
        return users_list

    def update_viewport_obj(self):
        self.viewport_obj = Viewport(resolution=self.config.fov_resolution,
                                     fov=self.config.fov,
                                     projection=self.proj_obj)

    def update_proj_obj(self):
        proj = self.proj_type[self.projection]
        self.proj_obj = proj(proj_res=self.config.resolution,
                             tiling=self.tiling)

    def init_player(self):
        ...
