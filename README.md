# py360tools Viewer

## Descrição

Um visualizador de demonstração da emulação do streming de vídeo 360º com ladrilhos. Disponível em: [Github - Py360tools Viewper](https://github.com/henriquedgarcia/py360tools_viewer) 

<img src="docs/img/py360tools_ui.png" alt="Descrição" width="300"/>

O py360tools Viewer recebe uma lista com os ladrilhos que serão vistos neste chunk e abre dois streams: um com a qualidade selecionada e outro de referência.
São calculados os MSEs dos ladrilhos e então calculada a média entre eles. 
Em seguida as projeções são extraídas o viewport que é usado par calcular o MSE.
Além do MSE médio dos ladrilhos e do MSE do viewport o visualizador ainda exibe o número de ladrilhos selecionados e sua taxa de bits.

<img src="docs/img/aplicacao.png" alt="Descrição" width="300"/>

O JSON de entrada deve conter algumas informações básicas sobre as representações disponíveis, de forma semelhante ao DASH.

O segment_template deve conter obrigatoriamente as chaves:

- {tile} - Um identificador (espacial) do arquivo de ladrilho
- {quality} - Um identificador (qualidade) do fator de qualidade usado na codificação
- {chunk} - Um identificador (temporal) do chunk que será acessado.

<img src="docs/img/json_config.png" alt="Descrição" width="300"/>

O dataset do movimento de cabeça deve ser um "Pandas DataFrame" com multiindex serializado com HDF5 (chave única). 
O dataset deve conter uma amostra por quadro. 
Os campos do índice são "nome", "usuario" e "frame". 
A tabela possui três colunas ("yaw", "pitch", "roll") em radianos.

<img src="docs/img/hm_dataset.png" alt="Descrição" width="300"/>

## Demonstração

### YouTube:
[<img src="docs/img/youtube_spam.png" alt="Descrição" width="300"/>](#!https://youtu.be/K38TKEvplYA)<br>
[https://youtu.be/K38TKEvplYA](#!https://youtu.be/K38TKEvplYA)
