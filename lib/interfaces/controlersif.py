from lib.interfaces.mainappbase import MainAppBase


class ControllersIf(MainAppBase):
    @property
    def menu(self):
        return self.main_app.menu

    @property
    def controls(self):
        return self.main_app.controls

    @property
    def checkboxes(self):
        return self.main_app.checkboxes

    @property
    def console(self):
        return self.main_app.console

    @property
    def config(self):
        return self.main_app.config

    @property
    def state(self):
        return self.main_app.state
