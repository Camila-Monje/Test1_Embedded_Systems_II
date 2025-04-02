#prueba
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

# Funciones del Pulsador
def detectar_pulsador():
    """Detecta si el pulsador está presionado"""
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Pulsador presionado (estado bajo)
        return True
    return False

def manejar_led_pulsador():
    """Maneja el encendido y apagado del LED basado en el pulsador"""
    if detectar_pulsador():
        ser.write(b'A')  # Enviar el carácter 'a' a la Tiva (cuando pulsador está presionado)
        print("Pulsador presionado, enviando 'A' a la Tiva (Encender LED).")
    else:
        ser.write(b'B')  # Enviar comando 4 a la Tiva (Apagar LED)
        print("Pulsador no presionado, enviando 'B' a la Tiva (Apagar LED).")

def loop_pulsador():
    """Monitorea el pulsador continuamente y envía comandos basados en su estado"""
    while True:
        manejar_led_pulsador()
        time.sleep(1)  # Espera 1 segundo antes de revisar nuevamente

# Función para mostrar el menú
def menu():
    print("\nSelecciona el código que quieres ejecutar:")
    print("1. Medir Distancia con Ultrasonido")
    print("2. Enviar comando basado en temperatura")
    print("3. Leer temperatura desde archivo")
    print("4. Detectar Pulsador")
    print("5. Controlar Intensidad de Luz")
    print("6. Salir")

def main():
    while True:
        menu()
        opcion = input("Ingresa el número de la opción: ").strip()
        print(f"Has seleccionado la opción: {opcion}")  # Impresión de depuración

        if opcion == '1':
            print("Iniciando medición de distancia...")  # Depuración adicional
            setup()
            try:
                loop_distancia()
            except KeyboardInterrupt:
                print("\nSaliendo del programa de distancia...")
                GPIO.cleanup()
                ser.close()
        elif opcion == '2':
            print("Iniciando lectura de temperatura...")  # Depuración adicional
            try:
                loop_temperatura()
            except KeyboardInterrupt:
                print("\nSaliendo del programa de temperatura...")
                ser.close()
        elif opcion == '3':
            print("Iniciando lectura desde archivo...")  # Depuración adicional
            try:
                loop_archivo_temperatura()
            except KeyboardInterrupt:
                print("\nSaliendo del programa de lectura de archivo...")
                ser.close()
        elif opcion == '4':
            print("Iniciando detección de pulsador...")  # Depuración adicional
            try:
                loop_pulsador()
            except KeyboardInterrupt:
                print("\nSaliendo del programa de pulsador...")
                GPIO.cleanup()
                ser.close()
        elif opcion == '5':
            print("Iniciando control de intensidad de luz...")  # Depuración adicional
            try:
                controlar_intensidad()
            except KeyboardInterrupt:
                print("\nSaliendo del programa de control de intensidad...")
                ser.close()
        elif opcion == '6':
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intenta nuevamente.")

if _name_ == "_main_":
    main()