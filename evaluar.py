import json
from modelo import cargar, generar, mensajes
from validador import validar

modelo, tokenizer = cargar()


def evaluar(fewshot):
    aciertos = 0
    for fila in open("datos/validacion.jsonl"):
        ejemplo = json.loads(fila)
        respuesta = generar(modelo, tokenizer, mensajes(ejemplo["incidencia"], fewshot))
        resultado = validar(respuesta, ejemplo["objetivo"])
        if resultado["categoria_correcta"] and resultado["prioridad_correcta"]:
            aciertos = aciertos + 1
    return aciertos


print("Básico:", evaluar(False), "/ 30")
print("Few-shot:", evaluar(True), "/ 30")
