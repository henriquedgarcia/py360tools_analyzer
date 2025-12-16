from lib.interfaces.controlersif import ControllersIf


class MainAppIf(ControllersIf):
    """Interface para a classe Main.
    Ela faz os controladores terem acesso o estado: (nome, projeção, tiling,
    qualidade, tile, chunk, frame, user, ...), e a configuração:

    """

    # main_app
    @property
    def app_root(self):
        return self.main_app.app_root

    # config
    @property
    def user_movement(self):
        return self.config.head_movement_data.loc[(self.state.video, self.state.user)]
