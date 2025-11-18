from lib.main import Main


class MainAppBase:
    main_app: Main

    def __init__(self, main_app: Main):
        self.main_app = main_app
