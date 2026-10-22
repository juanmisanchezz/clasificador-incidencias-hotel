# Contrato del clasificador de incidencias del hotel

## Categorías

- **habitacion**: problemas dentro de la habitación. **Ejemplos**: la tarjeta no abre, falta limpieza, ruido del vecino.
- **facturacion**: Error en el checking. Error en el cobro **Ejemplos**: Ha habido un error en el pago del checking y se ha cobrado de más. El cliente notifica que le han cobrado 2 veces en el minibar.
- **instalaciones**: Zonas comunes que se acaban rompiendo o deteriorando. Area de electricidad en el hotel. Fontanería. También las averías que afectan a varias habitaciones o a todo el hotel (agua, luz, ascensor); si la avería es solo dentro de una habitación, es **habitacion** **Ejemplos**: Parque infantil de las zonas comunes esta roto. Fallo en las máquinas de juegos. El lavamanos de zonas comunes se ha roto y no para de salir agua
- **consulta**: Preguntas e información general. Añadir una noche mas. Hora del desayuno. Informacion de eventos del hotel. Informacion de entrada y salidas **Ejemplos**: El cliente quiere añadir una noche mas. El cliente pregunta a que hora empieza y termina el desayuno. El cliente pregunta a que hora debe de hacer el checkout. El cliente pregunta cuando son los espectáculos.

## Prioridades

- **alta**: hay peligro, daños que van a más, el huésped no puede usar su habitación, o afecta a muchos huéspedes a la vez. **Ejemplos**: el parque infantil de las zonas comunes está roto, el lavamanos de zonas comunes no para de soltar agua, la tarjeta no abre.
- **media**: error de cobro, o el huésped no puede hacer algo normal de su estancia (dormir, ducharse con agua caliente, usar el ascensor) aunque pueda usar la habitación. **Ejemplos**: se ha cobrado de más en el check-in, le han cobrado 2 veces el minibar, falta limpieza, ruido del vecino.
- **baja**: preguntas, peticiones o fallos sin riesgo que pueden esperar. **Ejemplos**: fallo en las máquinas de juegos, añadir una noche más, horario del desayuno, hora del check-out, cuándo son los espectáculos.
- La palabra "urgente" sola no sube la prioridad.

## Formato de la respuesta

Solo un JSON, sin texto antes ni después:
{"categoria": "...", "prioridad": "...", "respuesta": "..."}

Ejemplo para "La tarjeta de mi habitación no abre la puerta y no puedo entrar":
{"categoria": "habitacion", "prioridad": "alta", "respuesta": "Lamentamos la molestia. Indíquenos su número de habitación para que recepción pueda revisarlo."}

- respuesta: una o dos frases amables en español. No promete reembolsos, plazos ni acciones que no se han hecho, y no pide datos de la tarjeta.
