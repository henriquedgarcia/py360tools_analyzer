import pandas as pd

# Abrir o DataFrame do arquivo HDF
df = pd.read_hdf('seuarquivo.h5')

# Verificar os níveis do MultiIndex
print(df.index.names)

# Identificar o nível constante
nivel_constante = 'nome_do_nivel_constante'  # substitua pelo nome correto

# Remover o nível constante do MultiIndex
df.index = df.index.droplevel(nivel_constante)

# Salvar o DataFrame novamente no HDF
df.to_hdf('seuarquivo_limpo.h5', key='nome_da_chave', mode='w')