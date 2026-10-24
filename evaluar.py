import json
from modelo import cargar, generar, mensajes
from validador import validar


def evaluar(modelo, tokenizer, fewshot, nombre):
    marcador = {"json_valido": 0, "categoria_correcta": 0, "prioridad_correcta": 0, "ambas": 0}
    salida = open("resultados/" + nombre + ".jsonl", "w")
    for fila in open("datos/test.jsonl"):
        ejemplo = json.loads(fila)
        respuesta = generar(modelo, tokenizer, mensajes(ejemplo["incidencia"], fewshot))
        resultado = validar(respuesta, ejemplo["objetivo"])
        if resultado["json_valido"]:
            marcador["json_valido"] = marcador["json_valido"] + 1
        if resultado["categoria_correcta"]:
            marcador["categoria_correcta"] = marcador["categoria_correcta"] + 1
        if resultado["prioridad_correcta"]:
            marcador["prioridad_correcta"] = marcador["prioridad_correcta"] + 1
        if resultado["categoria_correcta"] and resultado["prioridad_correcta"]:
            marcador["ambas"] = marcador["ambas"] + 1
        registro = {
            "id": ejemplo["id"],
            "incidencia": ejemplo["incidencia"],
            "esperado": ejemplo["objetivo"],
            "respuesta": respuesta,
            "resultado": resultado,
        }
        salida.write(json.dumps(registro, ensure_ascii=False) + "\n")
    salida.close()
    print(nombre, marcador)


modelo, tokenizer = cargar()
evaluar(modelo, tokenizer, False, "basico")
evaluar(modelo, tokenizer, True, "fewshot")

modelo, tokenizer = cargar("modelos/lora-hotel")
evaluar(modelo, tokenizer, False, "lora")
