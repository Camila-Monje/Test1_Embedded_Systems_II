import time
import serial
import os

# Configura el puerto serial
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
except serial.SerialException:
    print("No se pudo abrir el puerto UART. Verifica la conexión.")
    exit()

# Función para enviar el comando a la Tiva
def enviar_comando(comando):
    if comando == 2:
        ser.write(b'2')  # Enviar el carácter '2' a la Tiva (Encender motor)
        print("Comando '2' enviado: Encender motor")
    elif comando == 3:
        ser.write(b'3')  # Enviar el carácter '3' a la Tiva (Encender LED)
        print("Comando '3' enviado: Encender LED")
    elif comando == 4:
        ser.write(b'4')  # Enviar el carácter '4' a la Tiva (Apagar LED)
        print("Comando '4' enviado: Apagar LED")
    elif comando == 5:
        ser.write(b'5')  # Enviar el carácter '5' a la Tiva (Encender LED cuando pulsador presionado)
        print("Comando '5' enviado: Pulsador presionado, encender LED")
    elif isinstance(comando, str):  # Cuando se envía una letra (por intensidad)
        ser.write(comando.encode())  # Enviar el carácter (letra) a la Tiva
        print(f"Comando '{comando}' enviado a la Tiva (Intensidad de luz)")
    else:
        print("Comando no válido")

# Código 1: Medir Distancia con Ultrasonido
TRIG = 23
ECHO = 24

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

def medir_distancia():
    GPIO.output(TRIG, 0)
    time.sleep(0.00002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        pass
    time1 = time.time()

    while GPIO.input(ECHO) == 1:
        pass
    time2 = time.time()

    duracion = time2 - time1
    distancia = round((duracion * 343) / 2 * 100, 2)
    return int(distancia)

def enviar_estado(distancia):
    if distancia >= 7:
        estado = 0
    else:
        estado = 1

    # Envía el estado (0 o 1) como byte
    ser.write(str(estado).encode())
    print(f"Enviando: {estado} (Distancia: {distancia} cm)")

def loop_distancia():
    while True:
        dis = medir_distancia()
        enviar_estado(dis)
        time.sleep(0.8)

# Código 2: Enviar comando basado en temperatura
def fahrenheit_a_celsius(fahrenheit):
    return (fahrenheit - 32) * 5.0 / 9.0

def loop_temperatura():
    while True:
        temperatura = input("Ingresa la temperatura (con C o F): ").strip()

        # Comprobar si la entrada contiene "C" o "F"
        if temperatura[-1].upper() == 'C':
            temp_celsius = float(temperatura[:-1])
        elif temperatura[-1].upper() == 'F':
            temp_fahrenheit = float(temperatura[:-1])
            temp_celsius = fahrenheit_a_celsius(temp_fahrenheit)
        else:
            continue  # Si la unidad no es válida, vuelve a pedir la entrada

        # Tomar decisiones basadas en la temperatura en Celsius
        if temp_celsius > 20:
            enviar_comando(2)  # Enciende el motor
        elif temp_celsius < 2:
            enviar_comando(3)  # Enciende el LED
        else:
            enviar_comando(4)  # No enciende nada

        # Espera 1 segundo antes de solicitar otra temperatura
        time.sleep(1)

# Código 3: Leer temperatura desde archivo
def leer_temperatura():
    try:
        if os.path.exists("temperatura.txt"):
            with open("temperatura.txt", "r") as file:
                temperatura = file.readline().strip()  # Lee la primera línea del archivo
                return temperatura
        else:
            print("Archivo 'temperatura.txt' no encontrado.")
            return None  # Si el archivo no existe, retorna None
    except Exception as e:
        print(f"Error al leer el archivo 'temperatura.txt': {e}")
        return None  # Si ocurre un error al leer el archivo, retorna None

def loop_archivo_temperatura():
    while True:
        # Leer la temperatura desde el archivo
        temperatura = leer_temperatura()

        # Si no se pudo leer la temperatura, continuamos con el siguiente ciclo
        if temperatura is None:
            time.sleep(1)
            continue

        # Comprobar si la entrada contiene "C" o "F"
        if temperatura[-1].upper() == 'C':
            temp_celsius = float(temperatura[:-1])
        elif temperatura[-1].upper() == 'F':
            temp_fahrenheit = float(temperatura[:-1])
            temp_celsius = fahrenheit_a_celsius(temp_fahrenheit)
        else:
            print(f"Unidad de temperatura no válida en el archivo: {temperatura}")
            time.sleep(1)
            continue  # Si la unidad no es válida, vuelve a leer la temperatura

        # Tomar decisiones basadas en la temperatura en Celsius
        if temp_celsius > 20:
            enviar_comando(2)  # Enciende el motor
        elif temp_celsius < 2:
            enviar_comando(3)  # Enciende el LED
        else:
            enviar_comando(4)  # No enciende nada

        # Espera 1 segundo antes de leer la siguiente temperatura
        time.sleep(1)

# Función que ejecuta el código de la opción 1
def opcion_1():
    print("Iniciando medición de distancia...")
    setup()  # Configuración del GPIO para el ultrasonido
    try:
        loop_distancia()  # Medir distancia y enviar el estado
    except KeyboardInterrupt:
        print("\nSaliendo del programa de distancia...")
        GPIO.cleanup()
        ser.close()

# Función que ejecuta el código de la opción 2
def opcion_2():
    print("Iniciando lectura de temperatura...")
    try:
        loop_temperatura()  # Leer y tomar decisiones basadas en la temperatura
    except KeyboardInterrupt:
        print("\nSaliendo del programa de temperatura...")
        ser.close()

# Función que ejecuta el código de la opción 3
def opcion_3():
    print("Iniciando lectura desde archivo...")
    try:
        loop_archivo_temperatura()  # Leer temperatura desde archivo y tomar decisiones
    except KeyboardInterrupt:
        print("\nSaliendo del programa de lectura de archivo...")
        ser.close()

# Función para mostrar el menú
def menu():
    print("\nSelecciona el código que quieres ejecutar:")
    print("1. Medir Distancia con Ultrasonido")
    print("2. Enviar comando basado en temperatura")
    print("3. Leer temperatura desde archivo")
    print("4. Salir")

# Función principal para gestionar el menú
def main():
    while True:
        menu()
        opcion = input("Ingresa el número de la opción: ").strip()

        if opcion == '1':
            opcion_1()
        elif opcion == '2':
            opcion_2()
        elif opcion == '3':
            opcion_3()
        elif opcion == '4':
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intenta nuevamente.")

if __name__ == "__main__":
    main()
