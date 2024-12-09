import pickle
import pandas as pd

# Permite añadir información adicional a los datos de REASONER
# para poder ser utilizados en PEPLER.

# OUTPUT_DICT debe ser el diccionario resultado de generar 1 feature por review
# usando la API de GEMINI.

OUTPUT_DICT_PATH = ''
with open(OUTPUT_DICT_PATH, 'rb') as archivo:
    fs = pickle.load(archivo)

data = pd.read_csv('interaction.csv', sep='\t')

data['feature'] = ''

data.rename(columns={'user_id': 'user', 'video_id': 'item'}, inplace=True)

for (index, feature) in fs.items():
  data.iloc[index, data.columns.get_loc('feature')] = feature[0]

data.to_csv('interactions_pepler.csv', index=False)