import tkinter as tk
from tkinter import ttk, filedialog

# Para reprodução de vídeo, você precisará do OpenCV e Pillow
# Instale com: pip install opencv-python pillow
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VideoAnalysisApp:
    """
    Uma aplicação de GUI para análise de vídeo com gráficos e players.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Vídeo e Gráficos")
        self.root.geometry("1200x800")

        # --- Configuração do Layout Principal ---
        # A grade principal terá 2 colunas e 4 linhas
        # A coluna 0 (gráficos) será mais larga que a coluna 1 (vídeos)
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)

        # As linhas de vídeo terão altura fixa, a linha do gráfico se expandirá
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)  # Para o slider
        self.root.grid_rowconfigure(3, weight=0)  # Para os checkboxes

        # --- Variáveis de Controle ---
        self.video_path = None
        self.video_capture_full = None
        self.video_capture_tile = None
        self.checkbox_vars = {}

        # --- Criação dos Widgets ---
        self._create_menu()
        self._create_graph_area()
        self._create_video_players_area()
        self._create_tile_controls()
        self._create_settings_checkboxes()

    def _create_menu(self):
        """Cria a barra de menu superior."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir Vídeo...", command=self._open_video_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

    def _create_graph_area(self):
        """Cria a área de plotagem do Matplotlib à esquerda."""
        graph_frame = ttk.LabelFrame(self.root, text="Gráficos de Análise (Taxa de Bits, MSE, etc.)")
        # O gráfico ocupará as 3 primeiras linhas da coluna 0
        graph_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=10, pady=10)
        graph_frame.grid_rowconfigure(0, weight=1)
        graph_frame.grid_columnconfigure(0, weight=1)

        # Dados de exemplo para o gráfico
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x) * 1000 + 1500  # Exemplo de Taxa de Bits (kbps)
        y2 = np.cos(x) ** 2 * 30 + 5  # Exemplo de MSE

        ax.plot(x, y1, label="Taxa de Bits (kbps)")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Taxa de Bits (kbps)", color='tab:blue')
        ax.tick_params(axis='y', labelcolor='tab:blue')

        # Eixo Y secundário para MSE
        ax2 = ax.twinx()
        ax2.plot(x, y2, label="MSE", color='tab:red', linestyle='--')
        ax2.set_ylabel("MSE", color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        fig.suptitle("Métricas de Qualidade do Vídeo")
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        # Incorpora o gráfico no Tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _create_video_players_area(self):
        """Cria os dois players de vídeo à direita."""
        # --- Player de Vídeo Completo ---
        video_full_frame = ttk.LabelFrame(self.root, text="Vídeo Completo")
        video_full_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=(10, 5))
        video_full_frame.grid_rowconfigure(0, weight=1)
        video_full_frame.grid_columnconfigure(0, weight=1)

        self.video_full_label = ttk.Label(video_full_frame, background="black")
        self.video_full_label.grid(row=0, column=0, sticky="nsew")

        # --- Player de Tile de Vídeo ---
        video_tile_frame = ttk.LabelFrame(self.root, text="Tile do Vídeo")
        video_tile_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        video_tile_frame.grid_rowconfigure(0, weight=1)
        video_tile_frame.grid_columnconfigure(0, weight=1)

        self.video_tile_label = ttk.Label(video_tile_frame, background="black")
        self.video_tile_label.grid(row=0, column=0, sticky="nsew")

    def _create_tile_controls(self):
        """Cria o controle deslizante para o tamanho do tile."""
        slider_frame = ttk.LabelFrame(self.root, text="Tamanho do Tile")
        slider_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        slider_frame.grid_columnconfigure(0, weight=1)

        self.tile_size_slider = ttk.Scale(slider_frame, from_=10, to=100, orient="horizontal", command=self._on_slider_change)
        self.tile_size_slider.set(50)  # Valor inicial
        self.tile_size_slider.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    def _create_settings_checkboxes(self):
        """Cria as caixas de seleção na parte inferior."""
        settings_frame = ttk.LabelFrame(self.root, text="Configurações")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        options = [
            "Habilitar Super-Resolução",
            "Exibir Vetores de Movimento",
            "Destacar Bordas",
            "Aplicar Filtro de Cor"
            ]

        for i, option_text in enumerate(options):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(settings_frame, text=option_text, variable=var, command=self._on_checkbox_change)
            cb.pack(side="left", padx=10, pady=5)
            self.checkbox_vars[option_text] = var

    def _open_video_file(self):
        """Abre um arquivo de vídeo e inicia a reprodução."""
        self.video_path = filedialog.askopenfilename(
            title="Selecione um arquivo de vídeo",
            filetypes=(("Arquivos MP4", "*.mp4"), ("Arquivos AVI", "*.avi"), ("Todos os arquivos", "*.*"))
            )
        if not self.video_path:
            return

        # Libera capturas anteriores se existirem
        if self.video_capture_full:
            self.video_capture_full.release()
        if self.video_capture_tile:
            self.video_capture_tile.release()

        # Inicia novas capturas para ambos os players
        self.video_capture_full = cv2.VideoCapture(self.video_path)
        self.video_capture_tile = cv2.VideoCapture(self.video_path)

        # Inicia o loop de atualização dos frames
        self._update_full_video_frame()
        self._update_tile_video_frame()

    def _update_full_video_frame(self):
        """Lê um frame do vídeo completo, converte e exibe."""
        ret, frame = self.video_capture_full.read()
        if ret:
            # Redimensiona o frame para caber no label, mantendo a proporção
            label_w = self.video_full_label.winfo_width()
            label_h = self.video_full_label.winfo_height()

            if label_w > 1 and label_h > 1:  # Garante que o widget já tenha um tamanho
                frame_h, frame_w, _ = frame.shape
                ratio = min(label_w / frame_w, label_h / frame_h)
                new_dim = (int(frame_w * ratio), int(frame_h * ratio))
                frame = cv2.resize(frame, new_dim, interpolation=cv2.INTER_AREA)

            # Converte para um formato que o Tkinter possa usar
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_full_label.imgtk = imgtk
            self.video_full_label.configure(image=imgtk)

            # Repete a função após ~33ms (aproximadamente 30 FPS)
            self.root.after(33, self._update_full_video_frame)
        else:
            # Reinicia o vídeo quando chegar ao fim
            self.video_capture_full.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.root.after(33, self._update_full_video_frame)

    def _update_tile_video_frame(self):
        """Lê um frame, recorta o tile e exibe."""
        ret, frame = self.video_capture_tile.read()
        if ret:
            # Lógica para extrair o tile
            h, w, _ = frame.shape
            tile_size_percent = self.tile_size_slider.get() / 100.0
            tile_w = int(w * tile_size_percent)
            tile_h = int(h * tile_size_percent)

            # Pega o centro do frame como exemplo
            start_x = (w - tile_w) // 2
            start_y = (h - tile_h) // 2

            tile_frame = frame[start_y:start_y + tile_h, start_x:start_x + tile_w]

            # Redimensiona o tile para caber no label
            label_w = self.video_tile_label.winfo_width()
            label_h = self.video_tile_label.winfo_height()
            if label_w > 1 and label_h > 1 and tile_frame.size > 0:
                frame_h, frame_w, _ = tile_frame.shape
                ratio = min(label_w / frame_w, label_h / frame_h)
                new_dim = (int(frame_w * ratio), int(frame_h * ratio))
                tile_frame = cv2.resize(tile_frame, new_dim, interpolation=cv2.INTER_AREA)

            # Converte e exibe
            cv2image = cv2.cvtColor(tile_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_tile_label.imgtk = imgtk
            self.video_tile_label.configure(image=imgtk)

            self.root.after(33, self._update_tile_video_frame)
        else:
            # Reinicia o vídeo quando chegar ao fim
            self.video_capture_tile.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.root.after(33, self._update_tile_video_frame)

    def _on_slider_change(self, value):
        """Chamado quando o valor do slider muda."""
        # A lógica de atualização do tile já lê o valor do slider,
        # então não precisamos fazer nada extra aqui, mas o espaço está reservado.
        # print(f"Tamanho do tile alterado para: {float(value):.2f}%")
        pass

    def _on_checkbox_change(self):
        """Chamado quando uma caixa de seleção é marcada/desmarcada."""
        print("--- Estado das Configurações ---")
        for option, var in self.checkbox_vars.items():
            print(f"{option}: {'Ativado' if var.get() else 'Desativado'}")
        print("--------------------------")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnalysisApp(root)
    root.mainloop()
