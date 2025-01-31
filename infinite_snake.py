from machine import Pin, SoftI2C
import ssd1306
import time

# Configuración del I2C y la pantalla OLED
i2c = SoftI2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

def draw_spiral():
    x, y = 0, 0  # Punto inicial (esquina superior izquierda)
    width, height = 128, 64  # Dimensiones de la pantalla
    step = 2  # Paso para el crecimiento del remolino

    while width > 0 and height > 0:
        # Dibujar línea superior
        for i in range(x, x + width, step):
            display.pixel(i, y, 1)
            display.show()
            time.sleep(0.01)
        y += step  # Mover el borde superior hacia abajo

        # Dibujar línea derecha
        for i in range(y, y + height, step):
            display.pixel(x + width - 1, i, 1)
            display.show()
            time.sleep(0.01)
        width -= step  # Reducir el ancho de la espiral

        # Dibujar línea inferior
        for i in range(x + width - 1, x - 1, -step):
            display.pixel(i, y + height - 1, 1)
            display.show()
            time.sleep(0.01)
        height -= step  # Reducir la altura de la espiral

        # Dibujar línea izquierda
        for i in range(y + height - 1, y - 1, -step):
            display.pixel(x, i, 1)
            display.show()
            time.sleep(0.01)
        x += step  # Mover el borde izquierdo hacia la derecha

def erase_spiral():
    x, y = 0, 0
    width, height = 128, 64
    step = 2  # Paso para borrar el remolino

    while width > 0 and height > 0:
        # Borrar línea superior
        for i in range(x, x + width, step):
            display.pixel(i, y, 0)
            display.show()
            time.sleep(0.01)
        y += step

        # Borrar línea derecha
        for i in range(y, y + height, step):
            display.pixel(x + width - 1, i, 0)
            display.show()
            time.sleep(0.01)
        width -= step

        # Borrar línea inferior
        for i in range(x + width - 1, x - 1, -step):
            display.pixel(i, y + height - 1, 0)
            display.show()
            time.sleep(0.01)
        height -= step

        # Borrar línea izquierda
        for i in range(y + height - 1, y - 1, -step):
            display.pixel(x, i, 0)
            display.show()
            time.sleep(0.01)
        x += step

while True:
    draw_spiral()  # Dibuja el remolino
    time.sleep(1)  # Pausa para ver la espiral completa
    erase_spiral()  # Borra el remolino
    time.sleep(1)  # Pausa antes de repetir
