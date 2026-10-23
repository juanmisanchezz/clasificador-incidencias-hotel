from validador import validar

def test_json_bueno():
    texto = '{"categoria": "habitacion", "prioridad": "alta", "respuesta": "Lo sentimos"}'
    esperado = {"categoria": "habitacion", "prioridad": "alta"}
    resultado = validar(texto, esperado)
    assert resultado["json_valido"] == True
    assert resultado["categoria_correcta"] == True
    assert resultado["prioridad_correcta"] == True

def test_json_roto():
    texto = '{"categoria": "habitacion", "prioridad": "alta", "respuesta": "Lo sentimos"'
    esperado = {"categoria": "habitacion", "prioridad": "alta"}
    resultado = validar(texto, esperado)
    assert resultado["json_valido"] == False
    assert resultado["categoria_correcta"] == False
    assert resultado["prioridad_correcta"] == False

def test_categoria_mal():
    texto = '{"categoria": "consulta", "prioridad": "alta", "respuesta": "Lo sentimos"}'
    esperado = {"categoria": "habitacion", "prioridad": "alta"}
    resultado = validar(texto, esperado)
    assert resultado["json_valido"] == True
    assert resultado["categoria_correcta"] == False
    assert resultado["prioridad_correcta"] == True

def test_prioridad_mala():
    texto = '{"categoria": "habitacion", "prioridad": "baja", "respuesta": "Lo sentimos"}'
    esperado = {"categoria": "habitacion", "prioridad": "alta"}
    resultado = validar(texto, esperado)
    assert resultado["json_valido"] == True
    assert resultado["categoria_correcta"] == True
    assert resultado["prioridad_correcta"] == False