from machine import Pin, SoftI2C
import ssd1306
import time

# Configuración del I2C y la pantalla OLED
i2c = SoftI2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Posiciones y letras
x_pos = [5, 30, 55, 80, 105]  # Posiciones X de cada segmento
letters = "ERICK"  # Letras a mostrar

while True:
    # Llenar cada segmento con su letra correspondiente
    for i in range(5):
        display.fill_rect(x_pos[i], 10, 20, 40, 1)  # Llenar el segmento
        display.text(letters[i], x_pos[i] + 5, 25, 0)  # Dibujar la letra en color inverso
        display.show()
        time.sleep(1)

    # Limpiar los segmentos antes de repetir la animación
    for i in range(5):
        display.fill_rect(x_pos[i], 10, 20, 40, 0)  # Limpiar cada segmento
        display.show()
        time.sleep(0.5)





