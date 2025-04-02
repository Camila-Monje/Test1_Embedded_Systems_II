#funciones del switch de temperatura 

#envio de comandos para la toma de decisiones
def manejar_temperatura(temp_celsius):

    if temp_celsius > 20:
        enviar_comando(2)  # Enciende el motor
    elif temp_celsius < 2:
        enviar_comando(3)  # Enciende el LED
    else:
        enviar_comando(4)  # No enciende nada


#funcion de conversion de celsius a fahrenheit
def loop_temperatura():
    while True:
        temperatura = input("Ingresa la temperatura (con C o F): ").strip()

        if temperatura[-1].upper() == 'C':
            temp_celsius = float(temperatura[:-1])
        elif temperatura[-1].upper() == 'F':
            temp_fahrenheit = float(temperatura[:-1])
            temp_celsius = fahrenheit_a_celsius(temp_fahrenheit)
        else:
            continue 

        manejar_temperatura(temp_celsius)

        time.sleep(1)

