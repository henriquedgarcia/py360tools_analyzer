import tkinter as tk
from tkinter import ttk

from lib.interfaces.mainappif import MainAppIf
from lib.main import Main


class Console(MainAppIf):
    console_frame: ttk.Frame
    console_text: tk.Text
    scrollbar: tk.Scrollbar

    def __init__(self, main_app: Main):
        super().__init__(main_app)
        self._create_frame()
        self._create_text()

    def _create_frame(self):
        self.console_frame = ttk.Frame(self.app_root)
        self.console_frame.grid(row=2, column=0, padx=5, pady=15, sticky='nsew')
        self.console_frame.grid_rowconfigure(0, weight=0)
        self.console_frame.grid_columnconfigure(0, weight=1)

    def _create_text(self):
        # Widget de texto
        self.console_text = tk.Text(self.console_frame, wrap='word', height=7, width=50,
                                    font=('Courier New', 10)
                                    )

        self.scrollbar = tk.Scrollbar(self.console_frame)

        self.console_text.config(state='disabled', yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.console_text.yview)

        self.console_text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.print_console("Waiting for load config")

    def print_console(self, msg: str, end="\n"):
        self.console_text.config(state='normal')
        self.console_text.insert(tk.END, msg + end)
        self.console_text.config(state='disabled')
