
# Note that this is very bad 'weekend project'
# Python and is not at all representative
# of how things should be programmed in any 
# serious environment.

# This is snake on an ESP8266 with this
# I2C oled (I got it from here https://www.banggood.com/Geekcreit-WiFi-ESP8266-Starter-Kit-IoT-NodeMCU-Wireless-I2C-OLED-Display-DHT11-Temperature-Humidity-Sensor-Module-p-1544116.html)
# and an analog joystick (mine is from here https://www.banggood.com/Geekcreit-37-In-1-Sensor-Module-Board-Set-Starter-Kits-Geekcreit-products-that-work-with-official-Arduino-boards-p-1137051.html)

# Because the ESP8266 only has one analog 
# input data pin and I did not implement
import urandom
import sys
import utime
from ucollections import OrderedDict
from machine import Pin, I2C, PWM, sleep

if sys.implementation.name == 'micropython':
    import ssd1306
else:
    import adafruit_ssd1306 as ssd1306

# Configuración OLED
i2c = I2C(scl=Pin(5), sda=Pin(4))  # D1 (GPIO5) = SCL, D2 (GPIO4) = SDA
#oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
# Configuración de botones
joy_click = Pin(14, Pin.IN, Pin.PULL_UP)  # D5 (GPIO14)
joy_right = Pin(12, Pin.IN, Pin.PULL_UP)  # D6 (GPIO12)
joy_left = Pin(13, Pin.IN, Pin.PULL_UP)   # D7 (GPIO13)
mice = dict()
mousecount = 0
score = 0
mouse_amount = 4

SCORE_FILE = "scores.txt"

def read_joystick():
    return {
        'joy_click': not joy_click.value(),
        'joy_left': not joy_left.value(),
        'joy_right': not joy_right.value()
    }

def randint(min, max):
    span = max - min + 1
    div = 0x3fffffff // span
    offset = urandom.getrandbits(30) // div
    val = min + offset
    return val

def load_scores():
    try:
        with open(SCORE_FILE, "r") as f:
            return [line.strip().split(":") for line in f.readlines()]
    except:
        return []
# Funciones para manejar puntajes
def save_score(name, score):
    scores = load_scores()
    scores.append((name, score))
    scores = sorted(scores, key=lambda x: int(x[1]), reverse=True)[:5]
    with open(SCORE_FILE, "w") as f:
        for entry in scores:
            f.write(f"{entry[0]}:{entry[1]}\n")



def beep(beeplen):
    beeper = PWM(Pin(14), freq=440, duty=512)
    sleep(beeplen)
    beeper.deinit()


def draw(y, x):
    oled.pixel(x, y, 1)
    oled.show()


def show_scores():
    oled.fill(0)
    oled.text("Top 5 Scores", 20, 5)
    scores = load_scores()
    for i, (name, score) in enumerate(scores):
        oled.text(f"{i+1}. {name} {score}", 10, 15 + (i * 10))
    oled.show()
    utime.sleep(1)

# Función para capturar iniciales
def enter_initials(score):
    initials = ["A", "A", "A"]
    index = 0
    char_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    while index < 3:
        oled.fill(0)
        oled.text("Ingresa Iniciales:", 10, 10)
        oled.text(f"{initials[0]} {initials[1]} {initials[2]}", 50, 30)
        oled.text("^" if index == 0 else " ", 50, 40)
        oled.text("^" if index == 1 else " ", 60, 40)
        oled.text("^" if index == 2 else " ", 70, 40)
        oled.show()

        data = read_joystick()

        if data['joy_right']:
            initials[index] = char_list[(char_list.index(initials[index]) + 1) % len(char_list)]
        elif data['joy_left']:
            initials[index] = char_list[(char_list.index(initials[index]) - 1) % len(char_list)]
        elif data['joy_click']:
            index += 1

        utime.sleep(0.2)

    name = "".join(initials)
    save_score(name, score)
    oled.fill(0)
    oled.text(f"Guardado!", 30, 30)
    oled.show()
    utime.sleep(1)

# Función de Game Over
def game_over(score):
    oled.fill(0)
    oled.text("Game Over!", 20, 10)
    oled.text(f"Score: {score}", 30, 30)
    oled.text("Jugar(R)  Salir(L)", 10, 50)
    oled.show()

    scores = load_scores()
    if len(scores) < 5 or score > int(scores[-1][1]):
        enter_initials(score)

    

def update_score(score):
    for x in range(30):
        for y in range(10):
            oled.pixel(x, y, 0)
    oled.text("{}".format(score), 0, 0)


def draw_mouse(x, y, mousenr, size=4):
    global mice
    global mousecount
    draw_y = y
    for i_y in range(size):
        draw_x = x
        for i_x in range(size):
            mouse_x, mouse_y = draw_x + i_x, draw_y + i_y
            oled.pixel(mouse_x, mouse_y, 1)
            mice[(mouse_x, mouse_y)] = mousenr
    mousecount += 1


def generate_mice(amount=3):
    global mice
    global score
    offset = max(mice.values()) if mice else 0
    for mousenr in range(1, amount):
        if score < 100:
            max_size = 4
        elif score < 250:
            max_size = 6
        elif score < 1000:
            max_size = 8
        elif score < 2000:
            max_size = 10
        else:
            max_size = 12
        size = randint(4, max_size)
        x_rand = randint(size, oled_width - size)
        y_rand = randint(size, oled_height - size)
        draw_mouse(x_rand, y_rand, offset + mousenr, size=size)

# Juego como tal
def start_game():
    global mice
    global mousecount
    global score
    global mouse_amount
    oled.fill(0)
    grid = OrderedDict()
    snakelen = 15
    y = 32
    x = 64
    direction = 0
    prevscore = -1
    prevdata = read_joystick()
    generate_mice(3)
    while True:
        generate_mice(mouse_amount - mousecount)
        # snake hit itself
        if grid.get((x, y)):
            return

        # hit mouse
        mouse_nr = mice.get((x, y))
        if mouse_nr:
            mouse_blocks = []
            for mousexy, mousenr in mice.items():
                if mousenr == mouse_nr:
                    mouse_blocks.append(mousexy)
            for mousexy in mouse_blocks:
                del mice[mousexy]
                mouse_x, mouse_y = mousexy
                oled.pixel(mouse_x, mouse_y, 0)
                score += 1
            mouse_amount = randint(3, 5)
            mousecount -= 1
            beep(100)
            snakelen += 5

        grid[(x, y)] = 1
        while len(grid) > snakelen:
            snaketail_k, snaketail_v = list(grid.items())[0]
            snaketail_x, snaketail_y = snaketail_k
            oled.pixel(snaketail_x, snaketail_y, 0)
            del grid[(snaketail_x, snaketail_y)]

        draw(y, x)
        data = read_joystick()
        if data['joy_right'] and not prevdata['joy_right']:
            direction += 1
        if data['joy_left'] and not prevdata['joy_left']:
            direction -= 1
        if x > 127:
            x = 1
        if y > 63:
            y = 1
        if x < 1:
            x = 127
        if y < 1:
            y = 63
        if direction >= 4:
            direction = 0
        if direction < 0:
            direction = 3
        if direction == 0:
            x += 1
        if direction == 1:
            y += 1
        if direction == 2:
            x -= 1
        if direction == 3:
            y -= 1
        if score != prevscore:
            update_score(score)
        prevdata = data
        prevscore = score


while True:
    # Menú Principal
    oled.fill(0)
    oled.text('^', 20, 0)
    oled.text('^', 80, 0)
    oled.text('Bienvenido', 10, 20)
    oled.text('Jugar', 0, 10)
    oled.text('Score', 80, 10)
    oled.show()

    data = read_joystick()
    if data['joy_right']:
        start_game()
        game_over(score)
    if data['joy_left']:
        show_scores()
