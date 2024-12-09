# QxAIRecSys
Códigos del proyecto "Implementación de un método de evaluación cuantitativa de explicabilidad en Sistemas Recomendadores" desarrollado en el contexto del ramo "IIC3633 - Sistemas Recomendadores", en la Pontificia Universidad Católica de Chile (PUC).

## Descripción del repositorio

En este repositorio se encuentran los códigos de:

1. Una pequeña modificación a los códigos de REASONER que permiten obtener métricas de explicabilidad basadas en features para distintos sets de features.
2. Una modifiación específica a los códigos de PEPLER para ser entrenados sobre el dataset REASONER, utilizando para ello una herramienta de extracción de features.
3. Un script que utiliza los perfiles de usuario incluidos en el dataset REASONER para generar explicaciones/reviews.
4. Un script que utiliza la API de Gemini-flash 1.5 para extraer features de las reviews de REASONER, donde el número de features extraídas por review se puede ajustar (puede ser más de un feature por review)

## Como ejecutar

### PEPLER:

Desde la carpeta PEPLER:

Para PEPLER:

```
python -u main.py \
--data_path interactions_pepler.csv\
--index_dir ./ \
--cuda \
--checkpoint ./ >> logname.log
```

Para PEPLER-MLP:

```
python -u reg.py \
--data_path interactions_pepler.csv\
--index_dir ./ \
--cuda \
--checkpoint ./ >> logname.log
```

Para PEPLER-D:
 ```
python -u discrete.py \
--data_path interactions_pepler.csv\
--index_dir ./ \
--cuda \
--checkpoint ./ >> logname.log
```
(Recuerde modificar el nombre "logname.log" para no sobreescribir los resultados)

### REASONER:

Desde la carpeta REASONER:

```
python review_generate.py --model=[model name] --dataset=[dataset] --config=[config_files]
```

Ejemplo: 

```
python review_generate.py --model=PETER --dataset=3_core --config=properties/PETER.yaml
```

donde ```model```puede ser ```PETER```, ```NRT``` o ```Att2Seq```. 

### Llama-3:

Ejecutar primero `context.py` para obtener el contexto (perfil de los usuarios) y luego ejectuar `llama_api_reviews.py` para generar las reviews.

### Extraer features

Desde la carpeta de Gemini, ejecutar `feature_extraction.py` modificandolo para incluir una API_KEY de Gemini API. 

## Evaluar la calidad de texto de las reviews generadas

En la carpeta `TextQuality`, ejecutar `text_quality.py` incluyendo los archivos `.txt` de las reviews generadas en `TextQuality/generated`. Recuerde modificar los paths dentro de `text_quality.py`.

## Evaluación de la calidad de las explicaciones

Se calculan de manera automática al correr los modelos, quedando registradas en los correspondientes log. Las funciones para calcular dichas métricas se pueden encontrar en los correspondientes `utils.py` tanto para REASONER como PEPLER. 
Las métricas normalizadas se calculan utilizando dichas funciones.


REFERENCIAS:

```
@misc{chen2023reasoner,
      title={REASONER: An Explainable Recommendation Dataset with Multi-aspect Real User Labeled Ground Truths Towards more Measurable Explainable Recommendation}, 
      author={Xu Chen and Jingsen Zhang and Lei Wang and Quanyu Dai and Zhenhua Dong and Ruiming Tang and Rui Zhang and Li Chen and Ji-Rong Wen},
      year={2023},
      eprint={2303.00168},
      archivePrefix={arXiv},
      primaryClass={cs.IR}
}

@article{TOIS23-PEPLER,
	title={Personalized Prompt Learning for Explainable Recommendation},
	author={Li, Lei and Zhang, Yongfeng and Chen, Li},
	journal={ACM Transactions on Information Systems (TOIS)},
	year={2023}
}
```




