"""Genera los datos sintéticos 240/30/30 siguiendo contrato.md.

Train: 40 situaciones x 6 formas de escribirlas = 240 ejemplos.
Validación y test: 30 situaciones distintas cada uno, escritas una sola vez.
Cada situación es una "familia": una familia nunca aparece en dos grupos,
así el modelo no puede ver en train una paráfrasis de una pregunta del test.
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# Una respuesta fija por categoría: segura (no promete reembolsos ni plazos)
RESPUESTAS = {
    "habitacion": "Lamentamos la molestia. Indíquenos su número de habitación para que recepción pueda revisarlo.",
    "facturacion": "Indíquenos su número de habitación y el cargo que quiere revisar. No envíe datos de su tarjeta por este canal.",
    "instalaciones": "Gracias por avisar. Indíquenos el lugar exacto del hotel para que mantenimiento pueda revisarlo y, si hay peligro, aléjese de la zona.",
    "consulta": "Gracias por su mensaje. En recepción le darán la información actualizada sobre su consulta.",
}

# (incidencia, categoria, prioridad)
TRAIN = [
    ("La tarjeta de mi habitación no abre la puerta y no puedo entrar.", "habitacion", "alta"),
    ("Huele a humo dentro de mi habitación y no sé de dónde viene.", "habitacion", "alta"),
    ("La ducha de mi habitación pierde agua y el baño se está inundando.", "habitacion", "alta"),
    ("Mi habitación sigue sin limpiar desde ayer.", "habitacion", "media"),
    ("Los vecinos de la habitación de al lado hacen tanto ruido que no puedo dormir.", "habitacion", "media"),
    ("El aire acondicionado de mi habitación no enfría.", "habitacion", "media"),
    ("No hay toallas en el baño de mi habitación.", "habitacion", "media"),
    ("La televisión de mi habitación no tiene señal.", "habitacion", "baja"),
    ("¿Me podrían traer una almohada más a la habitación?", "habitacion", "baja"),
    ("La bombilla de la lámpara de noche está fundida.", "habitacion", "baja"),
    ("A todo nuestro grupo de la boda nos han cobrado la habitación dos veces.", "facturacion", "alta"),
    ("Me han cobrado dos veces el minibar.", "facturacion", "media"),
    ("En la factura aparece una cena que no hemos tomado.", "facturacion", "media"),
    ("Pagué en el check-in y me lo han vuelto a cobrar al salir.", "facturacion", "media"),
    ("Me han cobrado el parking y no he traído coche.", "facturacion", "media"),
    ("El importe de la factura no coincide con el precio de mi reserva.", "facturacion", "media"),
    ("¿Podéis hacerme la factura a nombre de mi empresa?", "facturacion", "baja"),
    ("¿Qué formas de pago aceptáis en recepción?", "facturacion", "baja"),
    ("¿Me podéis enviar la factura por email?", "facturacion", "baja"),
    ("Urgente: quiero saber si la tasa turística está incluida en el precio.", "facturacion", "baja"),
    ("El parque infantil de las zonas comunes está roto y es peligroso para los niños.", "instalaciones", "alta"),
    ("No hay agua caliente en toda la tercera planta.", "instalaciones", "alta"),
    ("El ascensor se ha parado con gente dentro.", "instalaciones", "alta"),
    ("Hay una fuga de agua en el pasillo de la segunda planta.", "instalaciones", "alta"),
    ("El wifi no funciona en todo el hotel.", "instalaciones", "alta"),
    ("El ascensor no funciona y tenemos que subir por la escalera.", "instalaciones", "media"),
    ("La piscina está cerrada por una avería y no podemos usarla.", "instalaciones", "media"),
    ("La máquina de café del vestíbulo no funciona.", "instalaciones", "baja"),
    ("Las máquinas de juegos de la sala recreativa están apagadas.", "instalaciones", "baja"),
    ("Una bombilla del pasillo está fundida.", "instalaciones", "baja"),
    ("¿A qué hora es el desayuno?", "consulta", "baja"),
    ("¿A qué hora tengo que hacer el check-out?", "consulta", "baja"),
    ("¿Puedo añadir una noche más a mi reserva?", "consulta", "baja"),
    ("¿Cuándo son los espectáculos de esta semana?", "consulta", "baja"),
    ("¿El hotel tiene parking?", "consulta", "baja"),
    ("¿Cómo llego al centro desde el hotel?", "consulta", "baja"),
    ("¿Se admiten mascotas en el hotel?", "consulta", "baja"),
    ("Gracias por todo, la estancia está siendo estupenda.", "consulta", "baja"),
    ("Tengo un problema, pero no sé muy bien cómo explicarlo.", "consulta", "baja"),
    ("Urgente: ¿a qué hora abre la piscina?", "consulta", "baja"),
]

VALIDACION = [
    ("La llave electrónica dejó de funcionar y estoy en el pasillo sin poder entrar.", "habitacion", "alta"),
    ("Sale agua del techo del baño de mi habitación y no para.", "habitacion", "alta"),
    ("Nadie ha hecho la cama hoy en mi habitación.", "habitacion", "media"),
    ("La calefacción de mi habitación no calienta.", "habitacion", "media"),
    ("Desde la habitación de arriba se oyen golpes toda la noche y no dormimos.", "habitacion", "media"),
    ("Al mando de la tele de mi habitación le faltan las pilas.", "habitacion", "baja"),
    ("¿Podrían subirme una manta extra?", "habitacion", "baja"),
    ("La cortina de la ventana de mi habitación no cierra del todo.", "habitacion", "baja"),
    ("A todos los huéspedes del congreso nos han cobrado el desayuno dos veces.", "facturacion", "alta"),
    ("Me han cargado una botella de vino del minibar que no he abierto.", "facturacion", "media"),
    ("Me habéis cobrado la cuna del bebé y no la pedimos.", "facturacion", "media"),
    ("El cargo en mi tarjeta es mayor que el total de la factura.", "facturacion", "media"),
    ("¿Me podéis dar la factura con el IVA desglosado?", "facturacion", "baja"),
    ("¿Se puede pagar en efectivo al salir?", "facturacion", "baja"),
    ("Urgente: ¿el precio de la habitación incluye la cena?", "facturacion", "baja"),
    ("Hay cristales rotos en el suelo junto a la piscina.", "instalaciones", "alta"),
    ("Se ha ido la luz en toda la segunda planta.", "instalaciones", "alta"),
    ("El ascensor hace ruidos raros y se para entre plantas.", "instalaciones", "alta"),
    ("La sauna del spa no se calienta y no podemos usarla.", "instalaciones", "media"),
    ("La máquina de hielo de la cuarta planta no funciona.", "instalaciones", "baja"),
    ("La fuente del jardín está apagada.", "instalaciones", "baja"),
    ("La puerta automática de la entrada tarda mucho en abrirse.", "instalaciones", "baja"),
    ("¿A qué hora cierra el restaurante?", "consulta", "baja"),
    ("¿Tenéis servicio de lavandería?", "consulta", "baja"),
    ("¿Puedo dejar las maletas en recepción después del check-out?", "consulta", "baja"),
    ("¿Organizáis excursiones desde el hotel?", "consulta", "baja"),
    ("¿El gimnasio está incluido en el precio?", "consulta", "baja"),
    ("Solo quería dar las gracias al personal de recepción.", "consulta", "baja"),
    ("Os escribo por un tema, pero no sé ni por dónde empezar.", "consulta", "baja"),
    ("Urgente: ¿a qué hora sale el autobús al aeropuerto?", "consulta", "baja"),
]

TEST = [
    ("La tarjeta no abre mi habitación y es la una de la madrugada.", "habitacion", "alta"),
    ("Huele a gas dentro de mi habitación.", "habitacion", "alta"),
    ("La habitación tiene polvo y el baño está sucio.", "habitacion", "media"),
    ("Hay una fiesta en la habitación de al lado y no podemos dormir.", "habitacion", "media"),
    ("No sale agua caliente en la ducha de mi habitación.", "habitacion", "media"),
    ("El secador de pelo de mi habitación no funciona.", "habitacion", "baja"),
    ("¿Pueden traerme más perchas a la habitación?", "habitacion", "baja"),
    ("La lámpara del escritorio de mi habitación parpadea un poco.", "habitacion", "baja"),
    ("Al grupo de la excursión nos han cargado a todos el traslado dos veces.", "facturacion", "alta"),
    ("Me han cobrado dos veces la cena del restaurante.", "facturacion", "media"),
    ("En la factura aparece un masaje del spa que no he recibido.", "facturacion", "media"),
    ("Al salir me cobraron una noche de más.", "facturacion", "media"),
    ("¿Me podéis mandar la factura de mi estancia por correo?", "facturacion", "baja"),
    ("¿Aceptáis pago con Bizum?", "facturacion", "baja"),
    ("Urgente: ¿el parking se paga aparte?", "facturacion", "baja"),
    ("Hay un cable eléctrico pelado en la zona de la piscina.", "instalaciones", "alta"),
    ("No hay agua en ninguna habitación de la primera planta.", "instalaciones", "alta"),
    ("Se ha inundado el garaje del hotel.", "instalaciones", "alta"),
    ("El ascensor está averiado y tenemos que subir andando.", "instalaciones", "media"),
    ("La piscina climatizada está fría porque se ha roto la caldera.", "instalaciones", "media"),
    ("Una máquina de juegos de la sala recreativa no enciende.", "instalaciones", "baja"),
    ("El televisor del bar no tiene sonido.", "instalaciones", "baja"),
    ("¿A qué hora empieza el desayuno el domingo?", "consulta", "baja"),
    ("¿Puedo hacer el check-out a las dos de la tarde?", "consulta", "baja"),
    ("¿Hay espectáculo esta noche?", "consulta", "baja"),
    ("¿Cómo puedo ir al aeropuerto desde el hotel?", "consulta", "baja"),
    ("¿Se puede reservar mesa en el restaurante?", "consulta", "baja"),
    ("Quería felicitar al equipo de limpieza.", "consulta", "baja"),
    ("Tengo una duda, pero no sé explicarla bien.", "consulta", "baja"),
    ("Urgente: ¿dónde está la farmacia más cercana?", "consulta", "baja"),
]

# Las 6 formas de escribir cada situación de train (cambia el texto, no la etiqueta)
FORMAS = [
    "{}",
    "Hola, {}",
    "Os escribo por lo siguiente: {}",
    "Buenas noches. {}",
    "{} ¿Me podéis ayudar?",
    "Perdonad la molestia: {}",
]


def fila(id_, familia, texto, categoria, prioridad):
    return {
        "id": id_,
        "familia": familia,
        "incidencia": texto,
        "objetivo": {
            "categoria": categoria,
            "prioridad": prioridad,
            "respuesta": RESPUESTAS[categoria],
        },
    }


def construir():
    train = []
    for n, (texto, categoria, prioridad) in enumerate(TRAIN):
        for forma in FORMAS:
            # Detrás de "Hola," o "Perdonad la molestia:" la frase sigue en minúscula
            frase = texto
            if forma.startswith(("Hola", "Perdonad")):
                # En "¿Me podrían…" la letra a cambiar es la segunda
                i = 1 if texto.startswith("¿") else 0
                frase = texto[:i] + texto[i].lower() + texto[i + 1 :]
            train.append(
                fila(f"TR-{len(train) + 1:03d}", f"train-{n:02d}", forma.format(frase), categoria, prioridad)
            )
    validacion = [
        fila(f"VA-{n + 1:02d}", f"validacion-{n:02d}", *caso) for n, caso in enumerate(VALIDACION)
    ]
    test = [fila(f"TE-{n + 1:02d}", f"test-{n:02d}", *caso) for n, caso in enumerate(TEST)]
    return {"train": train, "validacion": validacion, "test": test}


def comprobar(grupos):
    """Sin IDs ni textos repetidos y sin familias compartidas entre grupos."""
    ids, textos, familias = set(), set(), set()
    for nombre, filas in grupos.items():
        familias_aqui = set()
        for f in filas:
            texto = " ".join(f["incidencia"].casefold().split())
            if f["id"] in ids or texto in textos or f["familia"] in familias:
                raise ValueError(f"Repetido o mezclado entre grupos: {f['id']}")
            ids.add(f["id"])
            textos.add(texto)
            familias_aqui.add(f["familia"])
        familias |= familias_aqui
    return {nombre: len(filas) for nombre, filas in grupos.items()}


if __name__ == "__main__":
    grupos = construir()
    print(comprobar(grupos))
    (RAIZ / "datos").mkdir(exist_ok=True)
    for nombre, filas in grupos.items():
        texto = "".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas)
        (RAIZ / f"datos/{nombre}.jsonl").write_text(texto, encoding="utf-8", newline="\n")
