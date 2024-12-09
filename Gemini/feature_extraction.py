
import pandas as pd
import google.generativeai as genai
import time
import json
import pickle

'''
WARNING:
Dado que la API de Gemini Flash 1.5 carece de la posibilidad de 
establecer una random seed, el formato y contenido de los outputs
es variable. Por ende, puede que este código no funione directamente.
Las funciones que se encargan de procesar los datos están hardcodeadas
según la respuesta de Gemini.
'''
N = 1 # Indicar numero de features a extraer
OUTPUT_DICT_NAME = ''
FEATURE_SET_NAME = ''
TESTSET_NAME = ''
data = pd.read_csv('interaction.csv', sep='\t')
data = data[['user_id', 'video_id', 'rating', 'review']]
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# Tiempos de espera y largos están determinados por los límites de la API gratuita de Gemini.
i = 0
input = dict()
outputs = []
for review in reviews:
  input[f'Review_{i}'] = review
  i += 1
  query = 'Given the following reviews, extract up to ' + str(N) +' key features from each that represent the most important aspects of the item. \
  Your response should be a list of relevant, single-word features, separated by commas, directly derived from the review content. \
  Ensure the features are directly related to the item. \
  Input format: {Review_1: text, Review_2: text, ..., Review_n: text}. \
  Output format: JSON, structured as: {"Review_1": [features], "Review_2": [features], ..., "Review_n": [features]}, with no additional text or characters. \
  Input: ' + f'{input}'
  if len(query) >= 10**6/15:
    errors = 0
    while errors < 5:
      try:
        response = model.generate_content(query)
        outputs.append(response.text)
        print(response.text)
        time.sleep(60/15)
        input = dict()
        break
      except:
        time.sleep(10)
        errors += 1

out_dict = dict()
all_feat = []
numbers = []

# Procesar el texto obtenido para obtener un diccionario,
# que le asocia a cada id de review su(s) correspondiente(s) feature(s).
for j in range(len(outputs)):
  example=outputs[j].split('_')[1:]

  features = []
  for i in range(len(example)):
      features.append(example[i].rstrip(', "Review'))

  all_feat += features

for feat in all_feat:
  try:
    out_dict[int(feat.split(':')[0].rstrip('"'))] = json.loads(feat.split(':')[1])
  except:
    pass

# Feature set

vacum = []
for x in out_dict.values():
  if x != '':
    if x != []:
      vacum += x

vacum = [x.lower() for x in vacum if type(x) == str and x != '']
feature_s = set(vacum)

df_original = pd.read_csv('interaction.csv', sep='\t')
df_subset = pd.read_csv('test.csv', sep='\t')
matching_indices = df_original[df_original[['review']].isin(df_subset[['review']].to_dict(orient='list')).all(axis=1)].index

testset = []
fails = 0
for x in matching_indices:
  try:
    testset.append(feature_dict[x])
  except:
    testset.append([])
    fails += 1

with open(FEATURE_SET_NAME, 'wb') as archivo:
    pickle.dump(feature_s, archivo)
with open(OUTPUT_DICT_NAME, 'wb') as archivo:
    pickle.dump(out_dict, archivo)
with open(TESTSET_NAME, 'wb') as archivo:
    pickle.dump(testset, archivo)