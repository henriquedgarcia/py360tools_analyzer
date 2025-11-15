from tkinter import Label, StringVar, ttk

from lib.main import Main
from lib.mainappif import MainAppIf


class Comboboxes(MainAppIf):
    combo_dict: dict[str, ttk.Combobox]

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self._create_comboboxes_main_frame()
        self._create_comboboxes_inner_labeled_frame()
        self._create_settings_comboboxes()

    def _create_comboboxes_main_frame(self):
        self.settings_frame = ttk.Frame(self.app_root)
        self.settings_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

    def _create_comboboxes_inner_labeled_frame(self):
        self.video_frame = ttk.Labelframe(self.settings_frame, text='Video')
        self.video_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.projection_frame = ttk.Labelframe(self.settings_frame, text='Projeção')
        self.projection_frame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.tiling_frame = ttk.Labelframe(self.settings_frame, text='Tiling')
        self.tiling_frame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        self.quality_frame = ttk.Labelframe(self.settings_frame, text='Qualidade (QP)')
        self.quality_frame.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        self.users_frame = ttk.Labelframe(self.settings_frame, text='Usuário ID')
        self.users_frame.grid(row=0, column=4, padx=5, pady=5, sticky='ew')

        for idx in range(4):
            self.settings_frame.grid_columnconfigure(idx, weight=0)
        self.settings_frame.grid_columnconfigure(4, weight=1)

    video_name_string_var: StringVar

    def _create_settings_comboboxes(self):
        """Cria as caixas de seleção na parte inferior."""

        self.video_name_string_var = StringVar(value='---')
        self.projection_string_var = StringVar(value='---')
        self.tiling_string_var = StringVar(value='---')

        self.video_label = Label(self.video_frame, textvariable=self.video_name_string_var)
        self.projection_label = Label(self.projection_frame, textvariable=self.projection_string_var)
        self.tiling_label = Label(self.tiling_frame, textvariable=self.tiling_string_var)

        self.combo_dict = {'quality': ttk.Combobox(self.quality_frame, values=[], state='readonly'),
                           'user': ttk.Combobox(self.users_frame, values=[], state='readonly')}
        self.combo_dict['quality'].set('quality')
        self.combo_dict['user'].set('user')

        self.video_label.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.projection_label.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.tiling_label.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        self.combo_dict['quality'].grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        self.combo_dict['user'].grid(row=0, column=4, padx=5, pady=5, sticky='ew')
