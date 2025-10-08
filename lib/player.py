from tkinter import Tk, ttk, BooleanVar

dataset = {}  # 'head_movement'


def main():
    """
    A grade principal terá 5 linhas:
    1 - o menu que não é menu: tem dois botões "Abrir paths" e "Abrir HM"
    2 - tem 5 checkboxes:
        - Video ('cable_cam', 'closet_tour','pac_man','sunset')
        - Projeção ('erp', 'cmp')
        - Tiling
        - Qualidade
        - Usuário (depende do vídeo)
    3 - tem dois playes:
        player 1 - Projeção com os ladrilhos selecionados (60% da coluna)
        player 2 - Viewport extraído (40% da coluna)
    4 - tem três botões "reset", "play", "pause" para controlar o vídeo
    5 - Tem dois gráficos:
        esquerda (50% da coluna):
            gráficos gêmeos da série temporal (chunk) de bitrate/dectime dos chunks
        direita (50% da coluna):
            Gráficos gêmeos da série temporal (frame) de mse/ssim do viewport/projeção
    """
    app_root = Tk()
    config_main(app_root)
    create_menu(app_root)
    create_settings_comboboxes(app_root)
    create_players(app_root)
    create_controls(app_root)
    create_graphs(app_root)
    app_root.mainloop()


# def _on_right_side_container_resize(app_root):
#     # todo: ajustar esta função para que os frames do vídeo não varia de tamanho ao longo da reprodução. Não implementar ainda, apenas se necessário.
#     """
#     Atualiza as dimensões de exibição dos vídeos quando o contêiner da direita é redimensionado.
#     """
#     # Força o Tkinter a calcular os tamanhos internos dos widgets
#     app_root.update_idletasks()
#
#     # Atualiza as dimensões de exibição usando os tamanhos dos LabelFrames pais
#     # Agora, a altura será o valor fixo que definimos
#     video_display_w = video_frame.winfo_width()
#     video_display_h = video_frame.winfo_height()
#     viewport_display_w = viewport_frame.winfo_width()
#     viewport_display_h = viewport_frame.winfo_height()


def config_main(app_root):
    app_root.title("py360tools")
    app_root.geometry("1200x800")

    # --- Configuração do Layout Principal ---
    app_root.grid_rowconfigure(0, weight=1)  # menu abrir
    app_root.grid_rowconfigure(1, weight=1)  # Options
    app_root.grid_rowconfigure(2, weight=1)  # players
    app_root.grid_rowconfigure(3, weight=1)  # controle do player
    app_root.grid_rowconfigure(4, weight=1)  # gráficos


def create_menu(app_root):
    # todo: falta tudo
    ...


def create_settings_comboboxes(app_root):
    """Cria as caixas de seleção na parte inferior."""
    settings_frame = ttk.Labelframe(app_root, text="Config")
    settings_frame.grid(row=1, column=0, columnspan=1, sticky="nswe", padx=10, pady=10)  # Ajustado para row=1 da raiz
    combo_list: list[ttk.Combobox] = []
    for idx, col_name in enumerate(['name', 'projection', 'tiling', 'quality', 'user']):
        combo = ttk.Combobox(settings_frame, values=[], state="readonly")  # proj_list
        combo.set(col_name)
        combo.grid(row=0, column=idx, padx=5, pady=5)
        combo_list.append(combo)

    def select_user():
        name = combo_list[0].get()
        try:
            name_list = dataset['head_movement'].name.unique()
            if name in name_list:
                # O que é isso?
                combo_list[5].values = dataset['head_movement'].loc[(name,)].index.unique('users')
        except AttributeError:
            pass

    combo_list[5].configure(postcommand=select_user)


def create_players(app_root):
    # todo: Falta ajustar o frame dos vídeos
    video_container = ttk.Frame(app_root)
    video_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
    video_container.grid_columnconfigure(0, weight=1)  # Coluna única, ainda se expande horizontalmente
    video_container.grid_columnconfigure(1, weight=0)  # Coluna única, ainda se expande horizontalmente

    # video_container.bind('<Configure>', _on_right_side_container_resize)

    """Cria os dois players de vídeo à direita."""
    # Contêiner para os players de vídeo e o controle
    projection_frame = ttk.LabelFrame(video_container, text="projeção e ladrilhos")
    projection_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Configura as linhas dentro do contêiner da direita
    video_container.grid_rowconfigure(0, weight=0)  # Vídeo Completo (altura fixa)
    video_container.grid_rowconfigure(1, weight=0)  # Tile do Vídeo (altura fixa)
    video_container.grid_rowconfigure(2, weight=0)  # Slider (não se expande)
    video_container.grid_columnconfigure(0, weight=1)  # Coluna única, ainda se expande horizontalmente
    # video_container.bind('<Configure>', _on_right_side_container_resize)

    # --- Player de Viewport ---
    viewport_frame = ttk.LabelFrame(app_root, text="Tile do Vídeo")
    viewport_frame.config(height=190)  # Exemplo de altura fixa em pixels
    viewport_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=5)
    viewport_frame.grid_propagate(False)  # Impede que o LabelFrame redimensione para o conteúdo
    viewport_frame.grid_rowconfigure(0, weight=1)  # O Label interno ainda se expande para preencher o frame
    viewport_frame.grid_columnconfigure(0, weight=1)
    video_tile_label = ttk.Label(viewport_frame, background="black")
    video_tile_label.grid(row=0, column=0, sticky="nsew")

    # --- Player de Vídeo ---
    video_frame = ttk.LabelFrame(app_root, text="Vídeo Completo")
    video_frame.config(height=190)  # Exemplo de altura fixa em pixels
    video_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 5))
    video_frame.grid_propagate(False)  # Impede que o LabelFrame redimensione para o conteúdo
    video_frame.grid_rowconfigure(0, weight=1)  # O Label interno ainda se expande para preencher o frame
    video_frame.grid_columnconfigure(0, weight=1)
    video_full_label = ttk.Label(video_frame, background="black")
    video_full_label.grid(row=0, column=0, sticky="nsew")


def create_controls(app_root):
    # todo: faltam implementar as funções de controle
    def rewind(): ...

    def stop(): ...

    def play_pause(): ...

    video_control_frame = ttk.LabelFrame(app_root, text="Tamanho do Tile")
    video_control_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=(5, 0))
    video_control_frame.grid_columnconfigure(0, weight=1)

    for column, text, command in enumerate(zip(["\u23EA", "\u23F9", "\u23F8"],
                                               [rewind, stop, play_pause])):
        button = ttk.Button(video_control_frame, text=text, command=command)
        button.grid(row=0, column=column, padx=0, sticky='ew')

    # botão de repeat
    repeat = BooleanVar(value=True)
    repeat_button = ttk.Checkbutton(video_control_frame, text="Repeat", variable=repeat)
    repeat_button.grid(row=1, column=0, padx=0)


def create_graphs(app_root):
    # todo: Falta tudo
    ...


if __name__ == "__main__":
    main()
