import time
from machine import Timer
from bluetooth import BLE, UUID
import ubinascii
import M5
from M5 import BtnA, BtnB

# === Konfiguracja M5StickC ===
M5.begin()
M5.Lcd.setRotation(3)
M5.Lcd.fillScreen(0xA81F)  # Jasny fioletowy
M5.Lcd.setTextColor(0xFFFF) # Biały kolor
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
    M5.Lcd.fillScreen(0xA81F)
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
    # Tutaj należy zrobić rzeczywiste połączenie przez gap_connect
    # i pobrać charakterystyki GATT dla RPM i Temp
    time.sleep(2)
    connected = True
    M5.Lcd.setCursor(10, 100)
    M5.Lcd.print("Połączono!")

# === Główna logika ===
if not scan_obd():
    # Nie znaleziono urządzenia – kończymy program
    M5.Lcd.setCursor(10, 80)
    M5.Lcd.print("Koniec programu.")
else:
    # Urządzenie znalezione – czekamy na przycisk A
    M5.Lcd.setCursor(10, 100)
    M5.Lcd.print("Naciśnij A aby połączyć")
    while not connected:
        M5.update()
        if BtnA.wasPressed():
            connect_obd()
        time.sleep(0.2)

# === Połączenie ustanowione – główny interfejs ===
display_mode = "RPM"

while connected:
    M5.update()
    M5.Lcd.fillScreen(0xA81F)
    M5.Lcd.setCursor(10, 10)

    # Tutaj należy odczytywać dane z OBD przez charakterystyki GATT
    if display_mode == "RPM":
        # rpm_value = ble.gatts_read(rpm_char_handle)
        rpm_value = 1500  # przykład na początek
        M5.Lcd.print(f"RPM: {rpm_value}")
    elif display_mode == "TEMP":
        # temp_value = ble.gatts_read(temp_char_handle)
        temp_value = 25
        M5.Lcd.print(f"Temp: {temp_value} C")

    # Zmiana wyświetlanej wartości przyciskiem B
    if BtnB.wasPressed():
        display_mode = "TEMP" if display_mode == "RPM" else "RPM"

    # Wyłączenie przy obu przyciskach
    if BtnA.wasPressed() and BtnB.wasPressed():
        M5.Lcd.fillScreen(0x0000)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("Wyłączanie...")
        break

    time.sleep(0.2)
import time
from machine import Timer
from bluetooth import BLE, UUID
import ubinascii
import M5
from M5 import BtnA, BtnB

# === Konfiguracja M5StickC ===
M5.begin()
M5.Lcd.setRotation(3)
M5.Lcd.fillScreen(0xA81F)  # Jasny fioletowy
M5.Lcd.setTextColor(0xFFFF) # Biały kolor
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
    M5.Lcd.fillScreen(0xA81F)
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
    # Tutaj należy zrobić rzeczywiste połączenie przez gap_connect
    # i pobrać charakterystyki GATT dla RPM i Temp
    time.sleep(2)
    connected = True
    M5.Lcd.setCursor(10, 100)
    M5.Lcd.print("Połączono!")

# === Główna logika ===
if not scan_obd():
    # Nie znaleziono urządzenia – kończymy program
    M5.Lcd.setCursor(10, 80)
    M5.Lcd.print("Koniec programu.")
else:
    # Urządzenie znalezione – czekamy na przycisk A
    M5.Lcd.setCursor(10, 100)
    M5.Lcd.print("Naciśnij A aby połączyć")
    while not connected:
        M5.update()
        if BtnA.wasPressed():
            connect_obd()
        time.sleep(0.2)

# === Połączenie ustanowione – główny interfejs ===
display_mode = "RPM"

while connected:
    M5.update()
    M5.Lcd.fillScreen(0xA81F)
    M5.Lcd.setCursor(10, 10)

    # Tutaj należy odczytywać dane z OBD przez charakterystyki GATT
    if display_mode == "RPM":
        # rpm_value = ble.gatts_read(rpm_char_handle)
        rpm_value = 1500  # przykład na początek
        M5.Lcd.print(f"RPM: {rpm_value}")
    elif display_mode == "TEMP":
        # temp_value = ble.gatts_read(temp_char_handle)
        temp_value = 25
        M5.Lcd.print(f"Temp: {temp_value} C")

    # Zmiana wyświetlanej wartości przyciskiem B
    if BtnB.wasPressed():
        display_mode = "TEMP" if display_mode == "RPM" else "RPM"

    # Wyłączenie przy obu przyciskach
    if BtnA.wasPressed() and BtnB.wasPressed():
        M5.Lcd.fillScreen(0x0000)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("Wyłączanie...")
        break

    time.sleep(0.2)
