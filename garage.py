import RPi.GPIO as GPIO
import time
import serial
import os

# Configura el puerto serial
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
except serial.SerialException:
    print("No se pudo abrir el puerto UART. Verifica la conexión.")
    exit()

# Configuración del pulsador en GPIO
BUTTON_PIN = 18  # Configura el pin al que está conectado el pulsador

# Configurar el GPIO para el pulsador
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Entrada con resistencia pull-up

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

# Función para convertir un número de intensidad a letra
def convertir_a_letra(valor):
    """Convierte un número de intensidad en una letra ('c' a 'l')"""
    if 0 <= valor <= 1:
        return 'c'
    elif 2 <= valor <= 10:
        return 'd'
    elif 11 <= valor <= 20:
        return 'e'
    elif 21 <= valor <= 30:
        return 'f'
    elif 31 <= valor <= 40:
        return 'g'
    elif 41 <= valor <= 50:
        return 'h'
    elif 51 <= valor <= 60:
        return 'i'
    elif 61 <= valor <= 70:
        return 'j'
    elif 71 <= valor <= 80:
        return 'k'
    elif 81 <= valor <= 90:
        return 'l'
    else:
        return None  # Si el valor es mayor a 90 o menor a 0, no hay correspondencia

# Leer intensidad desde archivo
def leer_intensidad():
    try:
        if os.path.exists("intensidad.txt"):
            with open("intensidad.txt", "r") as file:
                intensidad = file.readline().strip()  # Lee la primera línea del archivo
                try:
                    intensidad_numero = int(intensidad)  # Convertimos el valor leído en un número
                    return intensidad_numero
                except ValueError:
                    print(f"El valor '{intensidad}' no es un número válido.")
                    return None
        else:
            print("Archivo 'intensidad.txt' no encontrado.")
            return None  # Si el archivo no existe, retorna None
    except Exception as e:
        print(f"Error al leer el archivo 'intensidad.txt': {e}")
        return None  # Si ocurre un error al leer el archivo, retorna None

# Función que controla la intensidad de luz
def controlar_intensidad():
    """Lee la intensidad desde el archivo y la convierte a una letra para enviarla a la Tiva"""
    intensidad = leer_intensidad()

    if intensidad is not None:
        letra = convertir_a_letra(intensidad)  # Convertir el número en una letra
        if letra:
            enviar_comando(letra)  # Enviar la letra de intensidad a la Tiva
            print(f"Intensidad leída: {intensidad}, convertida a: {letra}, enviada a la Tiva.")
        else:
            print(f"Valor de intensidad fuera del rango permitido: {intensidad}")
    else:
        print("No se pudo leer o encontrar un valor de intensidad válido.")

# Código 1: Medir Distancia con Ultrasonido (Sensor 1)
TRIG = 13
ECHO = 14

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

# Código 2: Medir Distancia con Ultrasonido (Sensor 2)
TRIG1 = 23
ECHO1 = 24

def setup1():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG1, GPIO.OUT)
    GPIO.setup(ECHO1, GPIO.IN)

def medir_distancia1():
    GPIO.output(TRIG1, 0)
    time.sleep(0.00002)
    GPIO.output(TRIG1, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG1, 0)

    while GPIO.input(ECHO1) == 0:
        pass
    time11 = time.time()

    while GPIO.input(ECHO1) == 1:
        pass
    time21 = time.time()

    duracion1 = time21 - time11
    distancia1 = round((duracion1 * 343) / 2 * 100, 2)
    return int(distancia1)

def enviar_estado1(distancia1):
    if distancia1 >= 10:
        estado1 = 5
    else:
        estado1 = 6

    # Envía el estado (5 o 6) como byte
    ser.write(str(estado1).encode())
    print(f"Enviando: {estado1} (Distancia: {distancia1} cm)")

def loop_distancia1():
    while True:
        dis = medir_distancia1()
        enviar_estado1(dis)
        time.sleep(0.8)

# Función para mostrar el menú
def menu():
    print("\nSelecciona el código que quieres ejecutar:")
    print("1. Medir Distancia con Ultrasonido (Sensor 1)")
    print("2. Medir Distancia con Ultrasonido (Sensor 2)")
    print("3. Controlar Intensidad de Luz")
    print("4. Detectar Pulsador")
    print("5. Salir")

def main():
    while True:
        menu()
        opcion = input("Ingresa el número de la opción: ").strip()
        print(f"Has seleccionado la opción: {opcion}")

        if opcion == '1':
            print("Iniciando medición de distancia con Sensor 1...")
            setup()
            try:
                loop_distancia()
            except KeyboardInterrupt:
                print("\nSaliendo del programa de distancia Sensor 1...")
                GPIO.cleanup()
                ser.close()
        elif opcion == '2':
            print("Iniciando medición de distancia con Sensor 2...")
            setup1()
            try:
                loop_distancia1()
            except KeyboardInterrupt:
                print("\nSaliendo del programa de distancia Sensor 2...")
                GPIO.cleanup()
                ser.close()
        elif opcion == '3':
            print("Iniciando control de intensidad de luz...")
            try:
                controlar_intensidad()
            except KeyboardInterrupt:
                print("\nSaliendo del programa de control de intensidad...")
                ser.close()
        elif opcion == '4':
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intenta nuevamente.")

if __name__ == "__main__":
    main()
