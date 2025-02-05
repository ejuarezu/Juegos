from machine import Pin, I2C
import ssd1306
import time

# Configurar la pantalla OLED
i2c = I2C(scl=Pin(5), sda=Pin(4))  # SCL en D1 (GPIO5), SDA en D2 (GPIO4)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Configurar botones como entradas con pull-up
btn1 = Pin(14, Pin.IN, Pin.PULL_UP)  # D5 = GPIO14
btn2 = Pin(12, Pin.IN, Pin.PULL_UP)  # D6 = GPIO12
btn3 = Pin(13, Pin.IN, Pin.PULL_UP)  # D7 = GPIO13

def mostrar_mensaje(mensaje):
    oled.fill(0)  # Borra la pantalla
    oled.text(mensaje, 10, 30)
    oled.show()

while True:
    if btn1.value() == 0:
        mostrar_mensaje("Botón 1 presionado")
    elif btn2.value() == 0:
        mostrar_mensaje("Botón 2 presionado")
    elif btn3.value() == 0:
        mostrar_mensaje("Botón 3 presionado")
    else:
        mostrar_mensaje("No hay botón presionado")

    time.sleep(0.1)  # Pequeño retardo para evitar rebotes
