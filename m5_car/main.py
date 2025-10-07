import time
from bluetooth import BLE
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

# === Zmienna do przechowywania znalezionych urządzeń ===
devices_found = []
connected = False

# --- Callback BLE do wykrywania OBD ---
def ble_irq(event, data):
    global devices_found
    if event == 5:  # advertising report
        addr_type, addr, adv_type, rssi, adv_data = data
        name = ble.resolve_name(adv_data) or "Nieznane"
        if "OBD" in name and name not in [d[0] for d in devices_found]:
            devices_found.append((name, addr))
            M5.Lcd.setCursor(10, 40)
            M5.Lcd.print(f"Znaleziono OBD: {name}")

ble.irq(ble_irq)

# --- Funkcja skanowania OBD ---
def scan_obd(timeout_ms=5000):
    devices_found.clear()
    M5.Lcd.fillScreen(0xF81F)
    M5.Lcd.setCursor(10, 10)
    M5.Lcd.print("Skanowanie OBD...")
    ble.gap_scan(timeout_ms, 30000, 30000)
    time.sleep((timeout_ms/1000)+1)
    ble.gap_scan(None)
    if not devices_found:
        M5.Lcd.setCursor(10, 60)
        M5.Lcd.print("Nie znaleziono OBD!")
        time.sleep(2)
        return False
    return True

# --- Funkcje odczytu PID (placeholder, zastąp prawdziwym BLE) ---
def read_rpm_from_obd():
    rpm = 1500 + int(5000 * abs(time.ticks_ms() % 1000 - 500)/500)
    return rpm

def read_temp_from_obd():
    temp = 70 + int(40 * abs(time.ticks_ms() % 1000 - 500)/500)
    return temp

def get_temp_color(temp_value):
    if temp_value < 75:
        return 0xF800       # czerwony
    elif 75 <= temp_value <= 87:
        return 0xFDA0       # pomarańczowy
    elif 88 <= temp_value <= 100:
        return 0x07E0       # zielony
    else:
        return 0x03E0       # ciemnozielony

def update_rpm_display(rpm_value):
    M5.Lcd.fillRect(0, 0, 160, 80, 0xF81F)
    M5.Lcd.setCursor(10, 10)
    M5.Lcd.setTextSize(4)
    M5.Lcd.print(f"RPM: {rpm_value}")

def update_temp_display(temp_value, color):
    M5.Lcd.fillScreen(color)
    M5.Lcd.setCursor(10, 10)
    M5.Lcd.setTextSize(4)
    M5.Lcd.print(f"Temp: {temp_value}C")
    if temp_value > 100:
        M5.Lcd.setCursor(10, 60)
        M5.Lcd.setTextSize(2)
        M5.Lcd.print("PRZEGRZANY!")

# === Główna logika programu ===
if not scan_obd():
    M5.Lcd.setCursor(10, 80)
    M5.Lcd.print("Koniec programu.")
else:
    # --- Menu funkcji ---
    menu_items = ["RPM", "Temperatura", "Wyjście"]
    menu_index = 0

    def draw_menu():
        M5.Lcd.fillScreen(0xF81F)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("Wybierz funkcję:")
        for i, item in enumerate(menu_items):
            prefix = ">" if i == menu_index else " "
            M5.Lcd.setCursor(10, 30 + i*20)
            M5.Lcd.print(f"{prefix} {item}")

    while True:
        draw_menu()
        M5.update()
        time.sleep(0.1)

        if BtnA.wasPressed():
            menu_index = (menu_index + 1) % len(menu_items)
        if BtnB.wasPressed():
            selection = menu_items[menu_index]

            if selection == "Wyjście":
                M5.Lcd.fillScreen(0x0000)
                M5.Lcd.setCursor(10, 10)
                M5.Lcd.setTextSize(2)
                M5.Lcd.print("Wyłączanie...")
                break

            elif selection == "RPM":
                last_rpm_time = time.ticks_ms()
                rpm_interval = 300  # ms
                prev_rpm = None
                while True:
                    now = time.ticks_ms()
                    if time.ticks_diff(now, last_rpm_time) >= rpm_interval:
                        last_rpm_time = now
                        rpm_value = read_rpm_from_obd()
                        if rpm_value != prev_rpm:
                            update_rpm_display(rpm_value)
                            prev_rpm = rpm_value

                    M5.update()
                    if BtnA.wasPressed() and BtnB.wasPressed():
                        break
                    time.sleep(0.05)

            elif selection == "Temperatura":
                last_temp_time = time.ticks_ms()
                temp_interval = 2000  # ms
                prev_temp = None
                prev_temp_color = None
                while True:
                    now = time.ticks_ms()
                    if time.ticks_diff(now, last_temp_time) >= temp_interval:
                        last_temp_time = now
                        temp_value = read_temp_from_obd()
                        temp_color = get_temp_color(temp_value)
                        if temp_value != prev_temp or temp_color != prev_temp_color:
                            update_temp_display(temp_value, temp_color)
                            prev_temp = temp_value
                            prev_temp_color = temp_color

                    M5.update()
                    if BtnA.wasPressed() and BtnB.wasPressed():
                        break
                    time.sleep(0.05)
