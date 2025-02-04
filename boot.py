import network
import urequests
import utime
import os
from machine import Pin, I2C
import ssd1306  # Asegúrate de tener este archivo en la memoria del ESP8266

# Configuración de la pantalla OLED
WIDTH = 128
HEIGHT = 64
i2c = I2C(scl=Pin(5), sda=Pin(4))  # D1 (GPIO5) = SCL, D2 (GPIO4) = SDA
oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Configuración WiFi
SSID = "Casa_JS"
PASSWORD = "FamJS2023!"
URL_MAIN = "https://raw.githubusercontent.com/ejuarezu/Juegos/main/main.py"

def mostrar_mensaje(linea1, linea2=""):
    """Muestra dos líneas de texto en la pantalla OLED."""
    oled.fill(0)  # Borra la pantalla
    oled.text(linea1, 0, 10)
    oled.text(linea2, 0, 30)
    oled.show()

def conectar_wifi():
    """Conecta a la red WiFi y muestra el estado en la OLED."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        mostrar_mensaje("Conectando a:", SSID)
        wlan.connect(SSID, PASSWORD)

        tiempo_espera = 10  # Máximo 10 segundos para conectar
        while not wlan.isconnected() and tiempo_espera > 0:
            utime.sleep(1)
            tiempo_espera -= 1

    if wlan.isconnected():
        mostrar_mensaje("WiFi Conectado", wlan.ifconfig()[0])
        return True
    else:
        mostrar_mensaje("Error WiFi", "Usando cache")
        return False

def descargar_main():
    """Descarga el archivo main.py si hay WiFi y lo guarda en la memoria."""
    try:
        mostrar_mensaje("Descargando", "main.py...")
        response = urequests.get(URL_MAIN)
        with open("main.py", "w") as f:
            f.write(response.text)
        response.close()
        mostrar_mensaje("Descarga OK")
    except Exception as e:
        mostrar_mensaje("Error descarga", str(e))

# Inicio del proceso
mostrar_mensaje("Iniciando...")

# Conectar WiFi y descargar main.py
if conectar_wifi():
    descargar_main()

# Mostrar mensaje final antes de ejecutar main.py
mostrar_mensaje("Ejecutando", "main.py")

utime.sleep(2)  # Espera antes de continuar con main.py