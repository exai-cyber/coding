import time
from machine import Timer
from bluetooth import BLE
import ubinascii
import M5
from M5 import BtnA, BtnB

# === Konfiguracja M5StickC ===
M5.begin()
M5.Lcd.setRotation(3)
M5.Lcd.fillScreen(0xF81F)  # Jasny fiolet
M5.Lcd.setTextColor(0xFFFF) # Biały
M5.Lcd.setTextSize(2)
M5.update()

# === BLE ===
ble = BLE()
ble.active(True)

OBD_NAME = "Twój_OBD_Name"  # wpisz nazwę swojego OBD
connected = False
conn_handle = None

devices_found = []

# Callback BLE
def ble_irq(event, data):
    global connected, conn_handle
    if event == 1:  # central connected
        conn_handle, _, _ = data
        connected = True
        M5.Lcd.setCursor(10, 60)
        M5.Lcd.print("Połączono z OBD!")
    elif event == 2:  # central disconnected
        connected = False
        conn_handle = None
        M5.Lcd.setCursor(10, 60)
        M5.Lcd.print("Rozłączono!")
    elif event == 5:  # advertising report
        addr_type, addr, adv_type, rssi, adv_data = data
        name = ble.resolve_name(adv_data) or "Nieznane"
        if name == OBD_NAME and name not in [d[0] for d in devices_found]:
            devices_found.append((name, addr))
            M5.Lcd.setCursor(10, 40)
            M5.Lcd.print(f"Znaleziono OBD: {name}")

ble.irq(ble_irq)

# Skanowanie urządzeń BLE
def scan_obd(timeout_ms=5000):
    devices_found.clear()
    M5.Lcd.fillScreen(0xF81F)
    M5.Lcd.setCursor(10, 10)
    M5.Lcd.print("Skanowanie OBD BLE...")
    ble.gap_scan(timeout_ms, 30000, 30000)
    time.sleep((timeout_ms / 1000) + 1)
    ble.gap_scan(None)
    if not devices_found:
        M5.Lcd.setCursor(10, 60)
        M5.Lcd.print("Nie znaleziono OBD!")
        return False
    return True

# Połączenie z pierwszym znalezionym OBD
def connect_obd():
    global conn_handle, connected
    name, addr = devices_found[0]
    M5.Lcd.setCursor(10, 80)
    M5.Lcd.print(f"Łączenie z {name}...")
    # Tutaj normalnie wywołujesz ble.gap_connect(addr_type, addr)
    # i pobierasz charakterystyki GATT RPM i Temp
    time.sleep(2)
    connected = True
    M5.Lcd.setCursor(10, 100)
    M5.Lcd.print("Połączono!")

# === Główna logika ===
if not scan_obd():
    M5.Lcd.setCursor(10, 80)
    M5.Lcd.print("Koniec programu.")
else:
    M5.Lcd.setCursor(10, 100)
    M5.Lcd.print("Naciśnij A aby połączyć")
    while not connected:
        M5.update()
        if BtnA.wasPressed():
            connect_obd()
        time.sleep(0.2)

# === Połączenie ustanowione – główny interfejs ===
display_mode = "RPM"
max_rpm = 8000  # do pseudo-animacji

while connected:
    M5.update()
    
    # Odczyt danych z OBD przez GATT - tu można podstawić właściwe odczyty
    if display_mode == "RPM":
        rpm_value = 1500 + int(5000 * abs(time.ticks_ms() % 1000 - 500)/500)
        M5.Lcd.fillRect(0, 0, 160, 80, 0xF81F)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.setTextSize(4)
        M5.Lcd.print(f"RPM: {rpm_value}")
    elif display_mode == "TEMP":
        temp_value = 70 + int(40 * abs(time.ticks_ms() % 1000 - 500)/500)
        # Kolor tła zależny od temperatury
        if temp_value < 75:
            color = 0xF800       # czerwony
        elif 75 <= temp_value <= 87:
            color = 0xFDA0       # pomarańczowy
        elif 88 <= temp_value <= 100:
            color = 0x07E0       # zielony
        else:  # > 100
            color = 0x03E0       # ciemnozielony
        M5.Lcd.fillScreen(color)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.setTextSize(4)
        M5.Lcd.print(f"Temp: {temp_value}C")
        if temp_value > 100:
            M5.Lcd.setCursor(10, 60)
            M5.Lcd.setTextSize(2)
            M5.Lcd.print("PRZEGRZANY!")

    # Zmiana wyświetlanej wartości przyciskiem B
    if BtnB.wasPressed():
        display_mode = "TEMP" if display_mode == "RPM" else "RPM"

    # Wyłączenie przy obu przyciskach
    if BtnA.wasPressed() and BtnB.wasPressed():
        M5.Lcd.fillScreen(0x0000)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.setTextSize(2)
        M5.Lcd.print("Wyłączanie...")
        break

    time.sleep(0.15)
