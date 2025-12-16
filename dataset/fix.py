import pandas as pd

# Abrir o DataFrame do arquivo HDF
df = pd.read_hdf('head_movement.hd5')

# Verificar os níveis do MultiIndex
print(df.index.names)

# Identificar o nível constante
df.index.names = ['video', 'user', 'frame']

# Salvar o DataFrame novamente no HDF
# df.to_hdf('head_movement_.hd5', key='head_movement', mode='w', complevel=9)
