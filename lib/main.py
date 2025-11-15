from tkinter import Tk
from typing import Optional

from py360tools import Tile

from lib.config import Config


class State:
    running: bool = False
    paused: bool = True
    video: str = None
    projection: str = None
    tiling: str = None
    quality: int = None
    user: int = None
    chunk: int = None
    frame: int = None
    tile: Optional[Tile] = None
    tile_ref: Optional[Tile] = None


class Main:
    """
    Esta classe representa a aplicação principal. Esta classe é o mais alto
    nível da aplicação e costumam ficar as variáveis globais que são os
    controladores (menu, comboboxes, video player, controls, graphs), o
    objeto Tk (app_root), o objeto com o estado (state) e o conteúdo do JSON
    (config). É nessa classe que executamos o mainloop do Tkinter.

    O construtor da class Main cria todos os controladores após o método
    self.config_main() inicializar o TKinter e definir sua configuração inicial,
    incluindo layout, geometria e título.

    O atributo state deve ser instanciado antes de qualquer controlador.
    A classe State poderia ser uma NamedTuple. É apenas uma classe para armazenar
    informações sobre a execução atual do programa, como video, projection, tiling,
    quality, tile, chunk, frame, user, paused, running, etc

    O atributo config não é iniciado e como atributo de classe possui valor None
    pois quem vai lhe atribuir alguma coisa é o controlador Menu assim que o
    usuário abrir um arquivo JSON. A classe Config transforma os itens do JSON
    em atributos da classe. Além disso, quando iniciada, ela já carrega o
    dataset de movimento de cabeça, calcula o número de quadros, converte a
    resolução e o FOV em tuplas e já cria os objetos Projection e Viewport,
    tanto de qualidade Q quanto de referência.

    No momento, o grid principal é composto de cinco linhas que conterão uma função
    diferente da GUI.

    - 1ª linha:
        + menu abrir JSON
        + todo: no futuro incluir novas opções
    - 2ª linha:
        + Um display que exibe o nome do vídeo, projeção e tiling.
        + Um Combobox para mudar a qualidade e o usuário.
    - 3ª linha:
        + canvas para exibir o vídeo da projeção
        + canvas para exibir o video do viewport
    - 4ª linha:
        + botões de controle play/pause, rewind, stop
        + checkbox para repeat
        + checkbox para não mostrar vídeo (apenas gráficos
    - 5ª linha:
        + um gráfico de eixo y gêmeos com bitrate e n_tiles
        + um gráfico de eixo y gêmeos com MSE médio dos ladrilhos e do viewport

    Um controlador é uma classe que cria e controla seu espaço na GUI. Por isso,
    todo controlador deve ser filho da classe MainIf. O controlador, ao ser
    instanciada recebe o self da classe Main. Com isso os controladores tem
    acesso a tudo da classe Main, incluindo os outros controladores, o config e
    o state.

    Para acessar outro controlador, o controlador deve herdar da classe de
    interface do controlador, ex: GraphIf, ComboIf, etc. Então o controlador
    acessa o atributo ou methods do outro controlador como se fosse seu.
    """
    state: State
    app_root: Tk
    config: Config = None

    def __init__(self):
        from lib.menu import Menu
        from lib.controlers.comboboxes import Comboboxes
        from lib.videoplayer import VideoPlayer
        from lib.controlers.controls import Controls
        from lib.controlers.graphs import Graphs

        self.config_main()

        self.menu = Menu(self)
        self.comboboxes = Comboboxes(self)
        self.video_player = VideoPlayer(self)
        self.controls = Controls(self)
        self.graphs = Graphs(self)
        self.app_root.mainloop()

    def config_main(self):
        self.state = State()
        self.app_root = Tk()
        self.app_root.geometry("1000x720")
        self.app_root.title('py360tools')

        self.app_root.grid_columnconfigure(0, weight=1)

        self.app_root.grid_rowconfigure(0, weight=0)  # menu abrir
        self.app_root.grid_rowconfigure(1, weight=0)  # Options
        self.app_root.grid_rowconfigure(2, weight=0)  # players
        self.app_root.grid_rowconfigure(3, weight=0)  # controle do player
        self.app_root.grid_rowconfigure(4, weight=1)  # gráficos


if __name__ == '__main__':
    Main()
