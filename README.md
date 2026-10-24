# Clasificador de incidencias de hotel con Qwen3-0.6B y LoRA

Proyecto 7 del máster de AI Engineering de thePower. *English version below.*

Trabajo de camarero en un hotel, así que elegí un problema que conozco: los clientes escriben quejas y preguntas, y alguien tiene que decidir de qué tipo son y con qué prisa hay que atenderlas. Quería ver si un modelo abierto muy pequeño, Qwen3-0.6B, podía hacerlo en mi propio Mac, y si entrenarlo merecía la pena frente a solo darle instrucciones.

Para cada mensaje el modelo tiene que devolver solo un JSON:

```json
{"categoria": "habitacion", "prioridad": "alta", "respuesta": "Lamentamos la molestia. Indíquenos su número de habitación para que recepción pueda revisarlo."}
```

Las categorías son (habitacion, facturacion, instalaciones y consulta), y las prioridades (alta, media y baja). Las reglas para decidir cada una están en [contrato.md](contrato.md), que escribí antes de hacer los datos.

El adaptador entrenado está publicado en Hugging Face: [juanmisanchezz/clasificador-incidencias-hotel-lora](https://huggingface.co/juanmisanchezz/clasificador-incidencias-hotel-lora).

## Las tres formas que comparo

1. Qwen con instrucciones: le paso las reglas del contrato resumidas en [prompts/basico.txt](prompts/basico.txt) y nada más.
2. Instrucciones y 5 ejemplos (few-shot): antes de cada mensaje le enseño 5 casos ya resueltos de entrenamiento, uno de cada categoría y con las tres prioridades. Los elegí una vez y no los volví a tocar ([prompts/fewshot-ids.json](prompts/fewshot-ids.json)).
3. Qwen con LoRA: lo entreno con los 240 ejemplos y luego le paso solo las instrucciones.

Las tres usan las mismas instrucciones y los mismos ajustes de generación (sin muestreo y como mucho 180 tokens), para que la comparación sea justa.

## Los datos

Son inventados, no hay mensajes de huéspedes reales. Los generé con [generar_datos.py](generar_datos.py) siguiendo el contrato:

- 240 de entrenamiento: 40 situaciones escritas de 6 formas distintas ("Hola, …", "Buenas noches. …").
- 30 de validación y 30 de test, con situaciones que no aparecen en entrenamiento.

El test no lo miré hasta el final. Para elegir los ejemplos del few-shot y ver si iba bien usé solo validación.

## Cómo está hecho

- [validador.py](validador.py) corrige una respuesta: mira si es un JSON válido (sin arreglarlo) y si acierta la categoría y la prioridad. Tiene 4 tests en `tests/`.
- [modelo.py](modelo.py) carga Qwen (con el adaptador si se lo paso), monta la conversación con o sin ejemplos y genera la respuesta.
- [entrenar_lora.py](entrenar_lora.py) entrena el LoRA. La pérdida solo se calcula sobre la respuesta, no sobre las instrucciones.
- [evaluar.py](evaluar.py) pasa los 30 de test por las tres formas y guarda cada respuesta tal cual en `resultados/`.
- [publicar.py](publicar.py) sube el adaptador a Hugging Face, lo vuelve a descargar y le hace una pregunta para comprobar que funciona.

El entrenamiento usa la configuración que daba el profesor, sin probar otros valores: r=8, alpha=16, 2 épocas y learning rate 0.0002. Tardó 11,8 minutos en mi MacBook Air M4 de 16 GB, con la GPU del Mac. La pérdida bajó de 0,98 a 0,02 y la de validación se quedó en 0,05, así que no estaba memorizando ([captura](capturas/6-entrenamiento-lora.png)).

## Resultados en test

Cuento un acierto cuando acierta la categoría y la prioridad a la vez.

| | JSON válido | Categoría | Prioridad | Las dos |
|---|---|---|---|---|
| Instrucciones | 30 | 23 | 9 | 6 |
| Few-shot | 30 | 22 | 18 | 14 |
| LoRA | 30 | 28 | 24 | 22 |

[Captura](capturas/7-resultados-test.png) · respuestas completas en `resultados/basico.jsonl`, `fewshot.jsonl` y `lora.jsonl`.

El JSON salió bien en todos los casos, así que las instrucciones ya bastaban para el formato. La categoría también la intuía casi siempre. Lo difícil era la prioridad: con solo instrucciones acertaba 9 de 30, con ejemplos 18 y entrenado 24. Mis reglas de prioridad (alta si hay peligro o el huésped no puede usar la habitación, media si hay un cobro mal hecho…) el modelo no las aplica bien leyéndolas; las aprende viendo muchos casos.

## Dónde sigue fallando el LoRA

De los 8 fallos, 6 son de prioridad, y en 5 de ellos el modelo dice "media" cuando no toca. Por ejemplo:

- "El secador de pelo de mi habitación no funciona" → dice media, debería ser baja.
- "Hay un cable eléctrico pelado en la zona de la piscina" → dice media, y es alta porque hay peligro. Este es el fallo que más me preocuparía en un hotel de verdad.
- "Al grupo de la excursión nos han cargado a todos el traslado dos veces" → dice media, pero afecta a muchos huéspedes, así que es alta.

Parece que, cuando duda, se queda en el medio. Los otros dos fallos son de categoría. Uno es "¿Aceptáis pago con Bizum?", que en mis datos puse como facturacion y el modelo dice consulta. Releyendo mi contrato, el modelo tiene bastante razón: es una pregunta, no un error de cobro. Ahí el fallo es más mío que suyo.

## Qué he aprendido

- Antes de entrenar hay que probar lo barato. En la vida real no pasaría directamente al LoRA: primero instrucciones, luego ejemplos y, si no basta, entrenar. Aquí sí hacía falta, porque con ejemplos se quedaba en 14 de 30.
- Con LoRA no se tocan los 600 millones de parámetros de Qwen. Se entrenan unas piezas pequeñas que van encima: el adaptador ocupa 20 MB frente a los 1,4 GB del modelo.
- Hay que formatear igual al entrenar y al preguntar. Uso la misma plantilla de chat con `enable_thinking=False` en los dos sitios; si no, el modelo aprendería un formato distinto del que luego le llega.
- Las etiquetas también pueden estar mal. Escribir el contrato antes de los datos me ayudó, pero el caso de Bizum demuestra que algunas reglas eran ambiguas.

## Cómo ejecutarlo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
cp .env.example .env        # y poner tu token de Hugging Face en HF_TOKEN
python -m pytest            # tests del validador
python entrenar_lora.py     # ~12 min en un Mac M4
python evaluar.py           # ~8 min
```

---

# Hotel incident classifier with Qwen3-0.6B and LoRA

Project 7 of thePower's AI Engineering master's.

I work as a waiter in a hotel, so I picked a problem I know: guests send complaints and questions, and someone has to decide what kind they are and how urgent. I wanted to see if a very small open model, Qwen3-0.6B, could do it on my own Mac, and whether fine-tuning was worth it compared to just giving it instructions.

For each message the model must return only a JSON with a category (room, billing, facilities or question), a priority (high, medium or low) and a short reply. The rules are in [contrato.md](contrato.md). The trained adapter is on Hugging Face: [juanmisanchezz/clasificador-incidencias-hotel-lora](https://huggingface.co/juanmisanchezz/clasificador-incidencias-hotel-lora).

I compared three setups with the same instructions and generation settings: instructions only, instructions plus 5 fixed examples (few-shot), and a LoRA adapter trained on 240 synthetic examples. Training used the course's fixed recipe (r=8, alpha=16, 2 epochs) and took 11.8 minutes on a MacBook Air M4 (16 GB).

Results on 30 unseen test cases (a hit means both category and priority are right):

| | Valid JSON | Category | Priority | Both |
|---|---|---|---|---|
| Instructions | 30 | 23 | 9 | 6 |
| Few-shot | 30 | 22 | 18 | 14 |
| LoRA | 30 | 28 | 24 | 22 |

The format was never the problem. Priority was: the model doesn't apply my priority rules just by reading them, but learns them from examples. The LoRA still misses 8 cases, mostly by answering "medium" when unsure, including a dangerous one (an exposed electric cable by the pool). One "error" (asking whether they accept Bizum) is really a labeling mistake on my side.

The data is synthetic and all in Spanish, and the test set is small, so this is a learning project, not something to use with real guests.
