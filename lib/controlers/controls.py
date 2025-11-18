from pathlib import Path
from tkinter import filedialog, ttk

from py360tools import AutoDict

from lib.interfaces.mainappif import MainAppIf
from lib.main import Main


class OpenControl(MainAppIf):
    def open(self):
        json_path = filedialog.askopenfilename(title='Selecione um arquivo',
                                               initialdir='./config/',
                                               filetypes=[('application/json',
                                                           '*.json')])
        json_path = Path(json_path)
        self.console.print_console(f"Opening config: {json_path}")
        self.config.open(json_path)


class SaveControl(MainAppIf):
    def save(self): ...


class CleanControl(MainAppIf):
    def clean(self): ...


class StopControl(MainAppIf):
    def stop(self): ...


class StartControl(MainAppIf):
    def start(self):
        self.console.print_console(f"Starting analysis...")
        self.start_chain()

    def start_chain(self):
        """
        + verificar se o dataset HMD
            - possui o vídeo em questão,
            - tem o formato correto (3 colunas 'yaw', 'pitch', 'roll')
            - só possui dois três níveis ('name', 'user', 'frame')
        + verificar arquivos de vídeo existem
            - fazer um LOOP e procurar todos os chunks se existem no formato:
            self.config.segment_template.format(video, projection, tiling,
            tile, quality, chunk)
        + rodar o pipeline em três LOOPs diferentes
            - Processar todos os tiles:
                [video]
                        [usuário][frame]
                            velocity
                        [projeção][tiling][chunk]
                                                [tile][quality]
                                                    check tiles
                                                [usuário]
                                                    get_seen_tiles
                                                    make_heatmap
                                                    [quality]
                                                        average tiles mse
                                                        viewport mse



            - Processar velocidade do usuário
                [video][usuário][frame]
            - Processar os tiles vistos
                [video][projeção][tiling][chunk][usuário]
            - Processar a qualidade dos tiles vistos (viewport)
                [video][projeção][tiling][chunk][usuário][quality]
        """

        self.configure_environment()
        self.check_hmd()
        self.check_chunks()
        self.run_loop()

    tiles_stats: AutoDict

    def configure_environment(self):
        self.tiles_stats = AutoDict()

    def check_hmd(self):
        pass

    def check_chunks(self):
        pass

    def run_loop(self):
        pass


class Controls(OpenControl, SaveControl, StartControl):
    """gerencia a quarta linha do aplicativo"""
    control_frame: ttk.LabelFrame

    def __init__(self, main_app: Main):
        super().__init__(main_app)
