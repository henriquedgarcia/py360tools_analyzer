import tkinter as tk
from tkinter import ttk, filedialog

# Para reprodução de vídeo, você precisará do OpenCV e Pillow
# Instale com: pip install opencv-python pillow
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# class VideoAnalysisApp:
#     """
#     Uma aplicação de GUI para análise de vídeo com gráficos e players.
#     """

#     def __init__(self, root):
#         self.root = root
#         self.root.title("Analisador de Vídeo e Gráficos")
#         self.root.geometry("1200x800")

#         # --- Configuração do Layout Principal ---
#         # A grade principal terá 2 colunas e 4 linhas
#         # A coluna 0 (gráficos) será mais larga que a coluna 1 (vídeos)
#         self.root.grid_columnconfigure(0, weight=3)
#         self.root.grid_columnconfigure(1, weight=1)

#         # As linhas de vídeo terão altura fixa, a linha do gráfico se expandirá
#         self.root.grid_rowconfigure(0, weight=1)
#         self.root.grid_rowconfigure(1, weight=1)
#         self.root.grid_rowconfigure(2, weight=0)  # Para o slider
#         self.root.grid_rowconfigure(3, weight=0)  # Para os checkboxes

#         # --- Variáveis de Controle ---
#         self.video_path = None
#         self.video_capture_full = None
#         self.video_capture_tile = None
#         self.checkbox_vars = {}

#         # --- Criação dos Widgets ---
#         self._create_menu()
#         self._create_graph_area()
#         self._create_video_players_area()
#         self._create_tile_controls()
#         self._create_settings_checkboxes()

#     def _create_menu(self):
#         """Cria a barra de menu superior."""
#         menu_bar = tk.Menu(self.root)
#         self.root.config(menu=menu_bar)

#         file_menu = tk.Menu(menu_bar, tearoff=0)
#         menu_bar.add_cascade(label="Arquivo", menu=file_menu)
#         file_menu.add_command(label="Abrir Vídeo...", command=self._open_video_file)
#         file_menu.add_separator()
#         file_menu.add_command(label="Sair", command=self.root.quit)

#     def _create_graph_area(self):
#         """Cria a área de plotagem do Matplotlib à esquerda."""
#         graph_frame = ttk.LabelFrame(self.root, text="Gráficos de Análise (Taxa de Bits, MSE, etc.)")
#         # O gráfico ocupará as 3 primeiras linhas da coluna 0
#         graph_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=10, pady=10)
#         graph_frame.grid_rowconfigure(0, weight=1)
#         graph_frame.grid_columnconfigure(0, weight=1)

#         # Dados de exemplo para o gráfico
#         fig = plt.figure()
#         ax = fig.add_subplot(111)
#         x = np.linspace(0, 10, 100)
#         y1 = np.sin(x) * 1000 + 1500  # Exemplo de Taxa de Bits (kbps)
#         y2 = np.cos(x) ** 2 * 30 + 5  # Exemplo de MSE

#         ax.plot(x, y1, label="Taxa de Bits (kbps)")
#         ax.set_xlabel("Tempo (s)")
#         ax.set_ylabel("Taxa de Bits (kbps)", color='tab:blue')
#         ax.tick_params(axis='y', labelcolor='tab:blue')

#         # Eixo Y secundário para MSE
#         ax2 = ax.twinx()
#         ax2.plot(x, y2, label="MSE", color='tab:red', linestyle='--')
#         ax2.set_ylabel("MSE", color='tab:red')
#         ax2.tick_params(axis='y', labelcolor='tab:red')

#         fig.suptitle("Métricas de Qualidade do Vídeo")
#         fig.tight_layout(rect=[0, 0.03, 1, 0.95])

#         # Incorpora o gráfico no Tkinter
#         canvas = FigureCanvasTkAgg(fig, master=graph_frame)
#         canvas.draw()
#         canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

#     def _create_video_players_area(self):
#         """Cria os dois players de vídeo à direita."""
#         # --- Player de Vídeo Completo ---
#         video_full_frame = ttk.LabelFrame(self.root, text="Vídeo Completo")
#         video_full_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=(10, 5))
#         video_full_frame.grid_rowconfigure(0, weight=1)
#         video_full_frame.grid_columnconfigure(0, weight=1)

#         self.video_full_label = ttk.Label(video_full_frame, background="black")
#         self.video_full_label.grid(row=0, column=0, sticky="nsew")

#         # --- Player de Tile de Vídeo ---
#         video_tile_frame = ttk.LabelFrame(self.root, text="Tile do Vídeo")
#         video_tile_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
#         video_tile_frame.grid_rowconfigure(0, weight=1)
#         video_tile_frame.grid_columnconfigure(0, weight=1)

#         self.video_tile_label = ttk.Label(video_tile_frame, background="black")
#         self.video_tile_label.grid(row=0, column=0, sticky="nsew")

#     def _create_tile_controls(self):
#         """Cria o controle deslizante para o tamanho do tile."""
#         slider_frame = ttk.LabelFrame(self.root, text="Tamanho do Tile")
#         slider_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
#         slider_frame.grid_columnconfigure(0, weight=1)

#         self.tile_size_slider = ttk.Scale(slider_frame, from_=10, to=100, orient="horizontal", command=self._on_slider_change)
#         self.tile_size_slider.set(50)  # Valor inicial
#         self.tile_size_slider.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

#     def _create_settings_checkboxes(self):
#         """Cria as caixas de seleção na parte inferior."""
#         settings_frame = ttk.LabelFrame(self.root, text="Configurações")
#         settings_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

#         options = [
#             "Habilitar Super-Resolução",
#             "Exibir Vetores de Movimento",
#             "Destacar Bordas",
#             "Aplicar Filtro de Cor"
#             ]

#         for i, option_text in enumerate(options):
#             var = tk.BooleanVar()
#             cb = ttk.Checkbutton(settings_frame, text=option_text, variable=var, command=self._on_checkbox_change)
#             cb.pack(side="left", padx=10, pady=5)
#             self.checkbox_vars[option_text] = var

#     def _open_video_file(self):
#         """Abre um arquivo de vídeo e inicia a reprodução."""
#         self.video_path = filedialog.askopenfilename(
#             title="Selecione um arquivo de vídeo",
#             filetypes=(("Arquivos MP4", "*.mp4"), ("Arquivos AVI", "*.avi"), ("Todos os arquivos", "*.*"))
#             )
#         if not self.video_path:
#             return

#         # Libera capturas anteriores se existirem
#         if self.video_capture_full:
#             self.video_capture_full.release()
#         if self.video_capture_tile:
#             self.video_capture_tile.release()

#         # Inicia novas capturas para ambos os players
#         self.video_capture_full = cv2.VideoCapture(self.video_path)
#         self.video_capture_tile = cv2.VideoCapture(self.video_path)

#         # Inicia o loop de atualização dos frames
#         self._update_full_video_frame()
#         self._update_tile_video_frame()

#     def _update_full_video_frame(self):
#         """Lê um frame do vídeo completo, converte e exibe."""
#         ret, frame = self.video_capture_full.read()
#         if ret:
#             # Redimensiona o frame para caber no label, mantendo a proporção
#             label_w = self.video_full_label.winfo_width()
#             label_h = self.video_full_label.winfo_height()

#             if label_w > 1 and label_h > 1:  # Garante que o widget já tenha um tamanho
#                 frame_h, frame_w, _ = frame.shape
#                 ratio = min(label_w / frame_w, label_h / frame_h)
#                 new_dim = (int(frame_w * ratio), int(frame_h * ratio))
#                 frame = cv2.resize(frame, new_dim, interpolation=cv2.INTER_AREA)

#             # Converte para um formato que o Tkinter possa usar
#             cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(cv2image)
#             imgtk = ImageTk.PhotoImage(image=img)

#             self.video_full_label.imgtk = imgtk
#             self.video_full_label.configure(image=imgtk)

#             # Repete a função após ~33ms (aproximadamente 30 FPS)
#             self.root.after(33, self._update_full_video_frame)
#         else:
#             # Reinicia o vídeo quando chegar ao fim
#             self.video_capture_full.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             self.root.after(33, self._update_full_video_frame)

#     def _update_tile_video_frame(self):
#         """Lê um frame, recorta o tile e exibe."""
#         ret, frame = self.video_capture_tile.read()
#         if ret:
#             # Lógica para extrair o tile
#             h, w, _ = frame.shape
#             tile_size_percent = self.tile_size_slider.get() / 100.0
#             tile_w = int(w * tile_size_percent)
#             tile_h = int(h * tile_size_percent)

#             # Pega o centro do frame como exemplo
#             start_x = (w - tile_w) // 2
#             start_y = (h - tile_h) // 2

#             tile_frame = frame[start_y:start_y + tile_h, start_x:start_x + tile_w]

#             # Redimensiona o tile para caber no label
#             label_w = self.video_tile_label.winfo_width()
#             label_h = self.video_tile_label.winfo_height()
#             if label_w > 1 and label_h > 1 and tile_frame.size > 0:
#                 frame_h, frame_w, _ = tile_frame.shape
#                 ratio = min(label_w / frame_w, label_h / frame_h)
#                 new_dim = (int(frame_w * ratio), int(frame_h * ratio))
#                 tile_frame = cv2.resize(tile_frame, new_dim, interpolation=cv2.INTER_AREA)

#             # Converte e exibe
#             cv2image = cv2.cvtColor(tile_frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(cv2image)
#             imgtk = ImageTk.PhotoImage(image=img)

#             self.video_tile_label.imgtk = imgtk
#             self.video_tile_label.configure(image=imgtk)

#             self.root.after(33, self._update_tile_video_frame)
#         else:
#             # Reinicia o vídeo quando chegar ao fim
#             self.video_capture_tile.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             self.root.after(33, self._update_tile_video_frame)

#     def _on_slider_change(self, value):
#         """Chamado quando o valor do slider muda."""
#         # A lógica de atualização do tile já lê o valor do slider,
#         # então não precisamos fazer nada extra aqui, mas o espaço está reservado.
#         # print(f"Tamanho do tile alterado para: {float(value):.2f}%")
#         pass

#     def _on_checkbox_change(self):
#         """Chamado quando uma caixa de seleção é marcada/desmarcada."""
#         print("--- Estado das Configurações ---")
#         for option, var in self.checkbox_vars.items():
#             print(f"{option}: {'Ativado' if var.get() else 'Desativado'}")
#         print("--------------------------")



import tkinter as tk
from tkinter import ttk # ttk para widgets mais modernos (como o Scale)
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class VideoAnalysisApp:
    def __init__(self, main_window):
        """
        Inicializa a aplicação de análise de vídeo.

        Args:
            main_window: A janela principal (root) do Tkinter.
        """
        self.main_window = main_window
        self.main_window.title("Análise de Vídeo e Gráficos")
        self.main_window.geometry("1200x800") # Tamanho inicial da janela (largura x altura)

        # Configura o redimensionamento das linhas e colunas do grid
        self._configure_grid_layout()

        self._create_menu()
        self._create_widgets()

    def _create_menu(self):
            """Cria a barra de menu superior."""
            menu_bar = tk.Menu(self.main_window)
            self.main_window.config(menu=menu_bar)

            file_menu = tk.Menu(menu_bar, tearoff=0)
            menu_bar.add_cascade(label="Arquivo", menu=file_menu)
            file_menu.add_command(label="Abrir Vídeo...", command=self._open_video_file)
            file_menu.add_separator()
            file_menu.add_command(label="Sair", command=self.main_window.quit)

    def _configure_grid_layout(self):
        """
        Configura o layout da grade (grid) para a janela principal.
        Define como as linhas e colunas se expandem.
        """
        # Permite que a coluna 0 (gráficos) e a linha 0 (gráficos) se expandam
        self.main_window.grid_rowconfigure(0, weight=0) # Nova linha para os botões (não se expande)
        self.main_window.grid_rowconfigure(1, weight=3) # Gráficos ocuparão mais espaço vertical
        self.main_window.grid_rowconfigure(2, weight=1) # Vídeos e controles ocuparão menos espaço vertical
        self.main_window.grid_rowconfigure(3, weight=0) # Slider e checkboxes não se expandem verticalmente
        self.main_window.grid_rowconfigure(4, weight=0) # Checkboxes
        self.main_window.grid_columnconfigure(0, weight=3) # Coluna dos gráficos/vídeo principal
        self.main_window.grid_columnconfigure(1, weight=1) # Coluna do tile
   
    def _create_buttons(self):
        self.frame_botoes = tk.Frame(self.main_window, bd=2, relief="flat", bg="#e8e8e8")
        self.frame_botoes.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # self.frame_botoes.grid_columnconfigure(0, weight=0) # Coluna dos botões (não se expande)
        # self.frame_botoes.grid_columnconfigure(1, weight=1) # Coluna dos nomes de arquivo (se expande)

        self.btn_opcao1 = tk.Button(self.frame_botoes, text="Carregar Dados", font=("Arial", 10), padx=10, pady=5, 
                                    command=self._on_button1_click, width=1)
        self.btn_opcao2 = tk.Button(self.frame_botoes, text="Processar Vídeo", font=("Arial", 10), padx=10, pady=5,
                                    command=self._on_button2_click, width=1)
        self.label_arquivo1 = tk.Label(self.frame_botoes, text="Nenhum arquivo carregado", font=("Arial", 10))
        self.label_arquivo2 = tk.Label(self.frame_botoes, text="Nenhum arquivo carregado", font=("Arial", 10))
        
        self.btn_opcao1.grid(row=0,column=0)
        self.btn_opcao2.grid(row=1, column=0)
        self.label_arquivo1.grid(row=0, column=1)
        self.label_arquivo2.grid(row=1, column=1)
        # self.btn_opcao1.pack(side=tk.LEFT, padx=5, pady=5)
        # self.btn_opcao2.pack(side=tk.RIGHT, padx=5, pady=5)
        # self.label_arquivo1.pack(side=tk.BOTTOM, padx=5, pady=5)
        # self.label_arquivo2.pack(side=tk.LEFT, padx=5, pady=5)


    def _create_widgets(self):
        """Cria e posiciona todos os widgets da interface."""
        # --- Nova Área para Botões Acima do Gráfico ---
        self._create_buttons()

        # --- 1. Área Grande para Gráficos Matplotlib ---
        self.frame_grafico = tk.Frame(self.main_window, bd=2, relief="groove", bg="#f0f0f0")
        self.frame_grafico.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot([0, 1, 2, 3, 4], [0, 2, 1, 3, 2], label="Taxa de Bits")
        self.ax.set_title("Gráfico de Desempenho (Exemplo)")
        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("Valor")
        self.ax.legend()
        self.ax.grid(True)

        self.canvas_grafico = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas_grafico.draw()
        self.canvas_grafico.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas_grafico, self.frame_grafico)
        self.toolbar.update()
        self.canvas_grafico.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # --- 2. Áreas para Reprodução de Vídeo (Placeholders) ---
        self.frame_videos = tk.Frame(self.main_window, bd=2, relief="groove", bg="#e0e0e0")
        self.frame_videos.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.frame_videos.grid_rowconfigure(0, weight=1)
        self.frame_videos.grid_columnconfigure(0, weight=1)
        self.frame_videos.grid_columnconfigure(1, weight=1)

        self.frame_video_full = tk.Frame(self.frame_videos, bd=2, relief="solid", bg="black")
        self.frame_video_full.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.label_video_full = tk.Label(self.frame_video_full, text="Vídeo Completo\n(Placeholder)",
                                        fg="white", bg="black", font=("Arial", 14),
                                        width=40, height=15)
        self.label_video_full.pack(expand=True, fill=tk.BOTH)

        self.frame_video_tile = tk.Frame(self.frame_videos, bd=2, relief="solid", bg="darkgrey")
        self.frame_video_tile.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.label_video_tile = tk.Label(self.frame_video_tile, text="Tile de Vídeo\n(Placeholder)",
                                       fg="white", bg="darkgrey", font=("Arial", 14),
                                       width=25, height=10)
        self.label_video_tile.pack(expand=True, fill=tk.BOTH)

        # --- 3. Controle Deslizante para o Tamanho do Tile ---
        self.frame_controles = tk.Frame(self.main_window, bd=2, relief="flat", bg="#f8f8f8")
        self.frame_controles.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.frame_controles.grid_columnconfigure(0, weight=1)

        self.label_slider = tk.Label(self.frame_controles, text="Ajustar Tamanho do Tile:", font=("Arial", 10))
        self.label_slider.pack(side=tk.LEFT, padx=5, pady=5)

        self.slider_tile = ttk.Scale(self.frame_controles, from_=50, to=200, orient=tk.HORIZONTAL,
                                     command=self._on_slider_change, length=300)
        self.slider_tile.set(100)
        self.slider_tile.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        # --- 4. Checkboxes para Configurações ---
        self.frame_checkboxes = tk.Frame(self.main_window, bd=2, relief="flat", bg="#f8f8f8")
        self.frame_checkboxes.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.frame_checkboxes.grid_columnconfigure(0, weight=1)

        self.var_opcao1 = tk.BooleanVar()
        self.var_opcao2 = tk.BooleanVar()
        self.var_opcao3 = tk.BooleanVar()

        self.chk_opcao1 = tk.Checkbutton(self.frame_checkboxes, text="Exibir Taxa de Bits", variable=self.var_opcao1,
                                        command=self._on_checkbox_change, font=("Arial", 10))
        self.chk_opcao2 = tk.Checkbutton(self.frame_checkboxes, text="Calcular MSE", variable=self.var_opcao2,
                                        command=self._on_checkbox_change, font=("Arial", 10))
        self.chk_opcao3 = tk.Checkbutton(self.frame_checkboxes, text="Habilitar Otimização", variable=self.var_opcao3,
                                        command=self._on_checkbox_change, font=("Arial", 10))

        self.chk_opcao1.pack(anchor=tk.W, padx=10, pady=2)
        self.chk_opcao2.pack(anchor=tk.W, padx=10, pady=2)
        self.chk_opcao3.pack(anchor=tk.W, padx=10, pady=2)

    # --- Métodos de Callback (agora são métodos da classe) ---

    def _on_slider_change(self, value):
        """Função chamada quando o controle deslizante do tile é movido."""
        print(f"Tamanho do Tile ajustado para: {value}")
        # Aqui você adicionaria a lógica para redimensionar o tile de vídeo

    def _on_checkbox_change(self):
        """Função chamada quando uma checkbox é alterada."""
        print("Estado das Checkboxes:")
        print(f"Opção 1: {self.var_opcao1.get()}")
        print(f"Opção 2: {self.var_opcao2.get()}")
        print(f"Opção 3: {self.var_opcao3.get()}")
        # Adicione sua lógica para cada configuração aqui

    def _on_button1_click(self):
        """Função chamada quando o Botão 1 é clicado."""
        print("Botão 'Carregar Dados' clicado!")
        self.label_arquivo1.config(text="arquivo_de_dados.csv")
        # Adicione sua lógica para o Botão 1 aqui

    def _on_button2_click(self):
        """Função chamada quando o Botão 2 é clicado."""
        print("Botão 'Processar Vídeo' clicado!")
        # Adicione sua lógica para o Botão 2 aqui
        self.label_arquivo2.config(text="arquivo_de_dados.csv")


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

# --- Bloco principal para executar a aplicação ---
if __name__ == "__main__":
    root = tk.Tk() # Cria a janela principal
    app = VideoAnalysisApp(root) # Instancia a classe da aplicação
    root.mainloop() # Inicia o loop principal do Tkinter
