import network
import ntptime
import time
import urequests
from machine import Pin, SoftI2C, RTC
import ssd1306

# Configuración del I2C y la pantalla OLED
i2c = SoftI2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Configuración del WiFi y zona horaria
SSID = "Casa_JS"
PASSWORD = "FamJS2024!"
UTC_OFFSET = -6  # Guatemala está en UTC-6
rtc = RTC()

# Tu API Key de OpenWeatherMap
API_KEY = '0b38cc37ae4634d25c9b3dc75926d83a'
CITY = 'Guatemala'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print(f"Conectando a WiFi {SSID}...")
    
    for _ in range(10):  # Intentar por 10 segundos
        if wlan.isconnected():
            print("Conexión exitosa! IP:", wlan.ifconfig()[0])
            return True
        time.sleep(1)
        print("Intentando conectar...")
    
    print("No se pudo conectar a WiFi.")
    return False

def sync_time():
    try:
        ntptime.settime()  # Sincroniza el tiempo con el servidor NTP
        print("Hora sincronizada con NTP.")
    except:
        print("No se pudo sincronizar con NTP. Usando hora almacenada.")

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=es"
    
    try:
        response = urequests.get(url)
        data = response.json()
        
        temp_c = data['main']['temp']
        condition = data['weather'][0]['description']
        
        return temp_c, condition
    except Exception as e:
        print("Error al obtener clima:", e)
        return None, None

def display_time_and_weather():
    while True:
        # Obtener la hora actual
        year, month, day, weekday, hour, minute, second, _ = rtc.datetime()

        # Ajustar la hora a la zona horaria de Guatemala (UTC-6) solo cuando la mostramos
        adjusted_hour = (hour + UTC_OFFSET) % 24  # Ajuste de hora por zona horaria

        # Mostrar hora y fecha ajustada
        display.fill(0)  # Limpiar pantalla
        time_str = "{:02}:{:02}:{:02}".format(adjusted_hour, minute, second)
        date_str = "{:02}/{:02}/{}".format(day, month, year)
        
        # Obtener clima
        temp_c, condition = get_weather()

        # Mostrar clima en la pantalla si los datos fueron obtenidos correctamente
        if temp_c is not None:
            display.text(f"Temp: {temp_c}C", 0, 0, 1)
            display.text(f"Cond: {condition}", 0, 10, 1)
        
        # Mostrar hora y fecha
        display.text(time_str, 20, 30, 1)
        display.text(date_str, 20, 50, 1)

        # Actualizar la pantalla
        display.show()

        time.sleep(1)

def main():
    if connect_wifi():
        sync_time()
    display_time_and_weather()

main()
