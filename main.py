import machine
import time
import ssd1306
import network
import os
import onewire
import ds18x20
import urequests
import ntptime
import math
#import framebuf
#import images_repo
#import utime

from machine import Pin, SoftI2C
# import sdcard
import ustruct
import random

# Configuración de pantalla OLED (I2C)
#i2c = machine.I2C(0, sda=Pin(4), scl=Pin(5), freq=20000)
i2c = SoftI2C(sda=Pin(4), scl=Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect("Casa_JS", "FamJS2024!")
        while not wlan.isconnected():
            pass
    print("Conectado a WiFi! Dirección IP:", wlan.ifconfig()[0])

conectar_wifi()
def draw_rotating_e():
    oled.fill(0)                         # fill entire screen with colour=0
    oled.rect(10, 10, 107, 43, 1)        # draw a rectangle outline 10,10 to width=107, height=53, colour=1

    # draw battery percentage
    x_pos = [12, 38, 64, 90]
    percentages = [.25, .50, .75, 1.0]
    while True:
        for ctr in range(4):
            oled.fill_rect(x_pos[ctr],11,24,40,1)
            oled.fill_rect(0,56,128,40,0)
            oled.text("{:.0%}".format(percentages[ctr]), 11, 56)
            oled.show()
            time.sleep_ms(2000)
        
        # This will clear the battery charge percentage
        for ctr in range(4):
            oled.fill_rect(x_pos[ctr],11,24,40,0)
            
        oled.show()

def draw_rotating_e_old():
    while True:
    for image in images_repo.images_list:
        buffer = image

        fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_HLSB)
        oled.fill(0)
        oled.blit(fb, 8, 0)

        oled.show()
        utime.sleep_ms(2000)
# Llamada a la función para empezar la animación
#draw_rotating_e()

print("inicio el programa")


# Configuración de DS18B20
ow = onewire.OneWire(Pin(12))  # GPIO12
ds = ds18x20.DS18X20(ow)
roms = ds.scan()  # Buscar todos los sensores DS18B20 conectados

# Configuración de botones
btn_left = Pin(14, Pin.IN, Pin.PULL_UP)  # GPIO14
btn_right = Pin(13, Pin.IN, Pin.PULL_UP)  # GPIO13
btn_select = Pin(0, Pin.IN, Pin.PULL_UP)  # GPIO0

# Configuración de la tarjeta SD
#sd = SD()
#os.mount(sd, '/sd')

# Variables del juego
snake = [(10, 10), (9, 10), (8, 10)]  # Inicializar la serpiente
direction = 'RIGHT'  # Dirección inicial
food = (5, 5)  # Comida
score = 0

# Función para obtener la hora y fecha desde Internet (hora de Guatemala)
def get_time():
    try:
        # Obtener hora de un servidor NTP
        ntptime.settime()
        
        # Ajustar a zona horaria de Guatemala (UTC-6)
        t = time.localtime(time.time() - 6 * 3600)
        return '{:02d}/{:02d}/{:04d} {:02d}:{:02d}:{:02d}'.format(t[2], t[1], t[0], t[3], t[4], t[5])
    except Exception as e:
        #oled.fill(0)
        #oled.text("Error al obtener", 0, 0)
        #oled.text("hora de Internet", 0, 10)
        #oled.show()
        time.sleep(3)
        return "Hora no disponible"

# Función para mostrar el menú
def show_menu():
    oled.fill(0)
    oled.text('Bienvenido Inge!', 0, 0)
    
    # Mostrar la hora y fecha
    current_time = get_time()
    #oled.text('Fecha y Hora:', 0, 10)
    oled.text(current_time, 0, 10)
    
    # Leer la temperatura
    try:
        #ds.convert_temp()
        print("test")
    except OSError:
        print("Error: No se pudo leer el sensor DS18X20. ¿Está conectado?")
        
    time.sleep(1)
    temperature = 0##ds.read_temp(roms[0])
    #oled.text('Temp: {} C'.format(temperature), 0, 30)

    # Mostrar opciones
    oled.text('1. Conectar WiFi', 0, 30)
    oled.text('2. Jugar Snake', 0, 40)
    oled.text('3. Descargar juegos', 0, 50)
    oled.show()

# Función para conectar a WiFi
def connect_wifi():
    oled.fill(0)
    oled.text('Conectando a WiFi...', 0, 0)
    oled.show()

    ssid = 'tuSSID'
    password = 'tuContraseña'
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        time.sleep(1)
        
    oled.fill(0)
    oled.text('Conectado a:', 0, 0)
    oled.text(ssid, 0, 10)
    oled.show()
    time.sleep(3)

# Función para el juego Snake
def snake_game():
    global snake, direction, food, score
    
    def draw_snake():
        for segment in snake:
            oled.rect(segment[0]*8, segment[1]*8, 8, 8, 1)
    
    def draw_food():
        oled.rect(food[0]*8, food[1]*8, 8, 8, 1)
    
    while True:
        oled.fill(0)
        draw_snake()
        draw_food()
        oled.text('Score: {}'.format(score), 0, 56)
        oled.show()
        
        # Detectar botones para movimiento
        if not btn_left.value():
            direction = 'LEFT'
        elif not btn_right.value():
            direction = 'RIGHT'
        elif not btn_select.value():
            return  # Regresar al menú principal
        
        # Mover la serpiente
        head_x, head_y = snake[0]
        if direction == 'RIGHT':
            head_x += 1
        elif direction == 'LEFT':
            head_x -= 1
        elif direction == 'UP':
            head_y -= 1
        elif direction == 'DOWN':
            head_y += 1
        
        # Comprobar si la serpiente colisiona con las paredes o con ella misma
        if head_x < 0 or head_y < 0 or head_x >= 16 or head_y >= 8 or (head_x, head_y) in snake:
            oled.fill(0)
            oled.text('Game Over', 0, 0)
            oled.text('Score: {}'.format(score), 0, 10)
            oled.show()
            time.sleep(3)
            return
        
        # Comprobar si la serpiente ha comido la comida
        if (head_x, head_y) == food:
            score += 1
            food = (random.randint(0, 15), random.randint(0, 7))  # Nueva comida
        else:
            snake.pop()  # Eliminar la cola de la serpiente
        
        snake.insert(0, (head_x, head_y))  # Mover la cabeza de la serpiente
        time.sleep(0.3)

# Función para descargar juegos desde GitHub
def download_game(game_url):
    oled.fill(0)
    oled.text('Descargando juego...', 0, 0)
    oled.show()
    
    # Descargar archivo de juego desde el repositorio
    response = urequests.get(game_url, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers['Content-Length'])
        downloaded = 0
        
        # Crear archivo en SD
        with open('/sd/' + game_url.split('/')[-1], 'wb') as f:
            while True:
                chunk = response.raw.read(1024)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                
                # Mostrar progreso
                progress = (downloaded / total_size) * 100
                oled.fill(0)
                oled.text('Descargando...', 0, 0)
                oled.text(f'{progress:.2f}% completado', 0, 10)
                oled.show()
                time.sleep(0.1)
        
        oled.fill(0)
        oled.text('Juego descargado', 0, 0)
        oled.show()
        time.sleep(3)
    else:
        oled.fill(0)
        oled.text('Error descargando', 0, 0)
        oled.text('el juego', 0, 10)
        oled.show()
        time.sleep(3)

# Función para listar juegos disponibles en la SD
def list_games():
    oled.fill(0)
    oled.text('Juegos disponibles:', 0, 0)
    
    # Listar archivos en la tarjeta SD
    files = os.listdir('/sd')
    games = [f for f in files if f.endswith('.py')]  # Filtrar solo archivos .py
    
    if not games:
        oled.text('No hay juegos', 0, 10)
    else:
        for i, game in enumerate(games):
            oled.text(f'{i+1}. {game}', 0, 10 + i*10)
    
    oled.show()
    time.sleep(3)

# Función para mostrar la lista de juegos desde el repositorio
def show_repo_games():
    oled.fill(0)
    oled.text('Cargando juegos...', 0, 0)
    oled.show()

    # Obtener lista de juegos desde el repositorio de GitHub
    repo_url = "https://api.github.com/repos/ejuarezu/Juegos/contents/"
    response = urequests.get(repo_url)
    
    if response.status_code == 200:
        files = response.json()
        games = [file['download_url'] for file in files if file['name'].endswith('.py')]  # Filtrar .py
        
        # Mostrar los juegos disponibles
        for i, game_url in enumerate(games):
            oled.fill(0)
            oled.text(f'{i+1}. Cargar juego {i+1}', 0, 0)
            oled.show()
            if not btn_select.value():
                download_game(game_url)
        oled.show()
    else:
        oled.fill(0)
        oled.text('Error obteniendo', 0, 0)
        oled.text('juegos del repo', 0, 10)
        oled.show()
        time.sleep(3)

# Main loop
while True:
    show_menu()
    
    if not btn_left.value():
        time.sleep(0.3)
        connect_wifi()
    elif not btn_right.value():
        time.sleep(0.3)
        snake_game()
    elif not btn_select.value():
        time.sleep(0.3)
        show_repo_games()
    time.sleep(0.1)
