//Me and ChatGPT : connecting with OBD2 via M5StickCPlus2 and displaying car statistics

#include <M5StickC.h>
#include "BluetoothSerial.h"

#define MAX_DEVICES 20

struct BTDevice {
  String name;
  String mac;
};

BTDevice devices[MAX_DEVICES];
int deviceCount = 0;
int selectedIndex = 0;

String ADRES_OBD2 = ""; // Uzupełnić

BluetoothSerial SerialBT;
bool btConnected = false;
uint16_t lightPurple;

// PID i etykiety do wyświetlania parametrów
String pids[] = {"010C","010D","0105","0104","012F","0136"};
String labels[] = {"RPM","Predkosc km/h","Temp silnika","Obciazenie silnika","Poziom paliwa","Cisnienie turbo"};
const int numParams = 6;
int buttonIndex = 0;

// Wyłączenie przy przytrzymaniu dwóch przycisków
unsigned long dualPressStart = 0;
const int dualPressTime = 2000; 

// Timer do nieblokującego odczytu PID
unsigned long lastUpdate = 0;
const int updateInterval = 200; // 5 razy na sekundę

void addDevice(String name, String mac) {
  if (deviceCount < MAX_DEVICES) {
    devices[deviceCount].name = name;
    devices[deviceCount].mac = mac;
    deviceCount++;
  }
}

String bdaddrToString(esp_bd_addr_t bda) {
  char buf[18];
  sprintf(buf, "%02X:%02X:%02X:%02X:%02X:%02X",
          bda[0], bda[1], bda[2], bda[3], bda[4], bda[5]);
  return String(buf);
}

// Callback GAP dla skanowania
void btGapCallback(esp_bt_gap_cb_event_t event, esp_bt_gap_cb_param_t *param) {
  if (event == ESP_BT_GAP_DISC_RES_EVT && deviceCount < MAX_DEVICES) {
    String addr = bdaddrToString(param->disc_res.bda);
    String name = "";

    for (int i = 0; i < param->disc_res.num_prop; i++) {
      auto p = param->disc_res.prop + i;
      if (p->type == ESP_BT_GAP_DEV_PROP_BDNAME) {
        char nm[248];
        memcpy(nm, (char *)p->val, p->len);
        nm[p->len] = 0;
        name = String(nm);
      }
    }

    if (name.length() == 0) name = "Bez nazwy";
    addDevice(name, addr);

    M5.Lcd.fillScreen(lightPurple);
    M5.Lcd.setTextColor(WHITE);
    M5.Lcd.setTextSize(2);
    M5.Lcd.setCursor(4, 8);
    M5.Lcd.print("Znaleziono:");
    M5.Lcd.setCursor(4, 32);
    M5.Lcd.print(name);
    M5.Lcd.setCursor(4, 56);
    M5.Lcd.print(addr);
  }
}

// Start skanowania
void startBtScan() {
  esp_bt_gap_start_discovery(ESP_BT_INQ_MODE_GENERAL_INQUIRY, 10, 0);
}

// Inicjalizacja ELM327
void initELM() {
  if (!btConnected) {
    M5.Lcd.fillScreen(lightPurple);
    M5.Lcd.setCursor(4, 30);
    M5.Lcd.print("Brak polaczenia BT");
    return;
  }

  auto sendAndShow = [&](const char* cmd, int waitMs=300) {
    SerialBT.print(cmd); SerialBT.print("\r");
    delay(waitMs);
    String resp = readBTResponse(800);
  };

  sendAndShow("ATZ", 800);
  sendAndShow("ATE0", 300);
  sendAndShow("ATL0", 300);
  sendAndShow("ATH0", 300);
  sendAndShow("ATSP0", 300);
}

// Odczyt odpowiedzi z adaptera
String readBTResponse(int timeoutMs) {
  String resp = "";
  unsigned long start = millis();
  while (millis() - start < timeoutMs) {
    while (SerialBT.available()) {
      char c = SerialBT.read();
      if (c != '\r' && c != '\n') resp += c;
    }
    if (resp.length() && (millis() - start) > 50) break;
    delay(10);
  }
  resp.trim();
  return resp;
}

// Odczyt PID
int readPID(String pid) {
  if (!btConnected) return -1;
  SerialBT.print(pid + "\r");
  delay(200);
  String resp = readBTResponse(500);
  resp.replace(" ", ""); resp.replace("\r",""); resp.replace("\n","");

  if (pid == "010C" && resp.length() >= 8 && resp.substring(0,4) == "410C") {
    int A = strtol(resp.substring(4,6).c_str(), nullptr, 16);
    int B = strtol(resp.substring(6,8).c_str(), nullptr, 16);
    return ((A*256)+B)/4;
  } else if (pid == "0105" && resp.length() >= 6 && resp.substring(0,4) == "4105") {
    int A = strtol(resp.substring(4,6).c_str(), nullptr, 16);
    return A - 40;
  } else if (pid == "010D" && resp.length() >= 6 && resp.substring(0,4) == "410D") {
    int A = strtol(resp.substring(4,6).c_str(), nullptr, 16);
    return A;
  } else if (pid == "0104" && resp.length() >= 6 && resp.substring(0,4) == "4104") {
    int A = strtol(resp.substring(4,6).c_str(), nullptr, 16);
    return A;
  } else if (pid == "012F" && resp.length() >= 6 && resp.substring(0,4) == "412F") {
    int A = strtol(resp.substring(4,6).c_str(), nullptr, 16);
    return A;
  } else if (pid == "0136" && resp.length() >= 6 && resp.substring(0,4) == "4136") {
    int A = strtol(resp.substring(4,6).c_str(), nullptr, 16);
    return A;
  }

  return -1;
}

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);
  M5.begin();
  M5.Lcd.setRotation(1);

  lightPurple = M5.Lcd.color565(200,150,255);
  M5.Lcd.fillScreen(lightPurple);
  M5.Lcd.setTextColor(WHITE);
  M5.Lcd.setTextSize(2);
  M5.Lcd.setCursor(4, 8);
  M5.Lcd.print("Skaner BT (Classic)");

  // Inicjalizacja BT Classic
  esp_bluedroid_init();
  esp_bluedroid_enable();
  esp_bt_gap_register_callback(btGapCallback);

  startBtScan();
}

// ---------------- LOOP ----------------
bool scannerDone = false;
void loop() {
  M5.update();

  // Wyłączenie przy przytrzymaniu dwóch przycisków
  if (M5.BtnA.isPressed() && M5.BtnB.isPressed()) {
    if (dualPressStart == 0) dualPressStart = millis();
    else if (millis() - dualPressStart > dualPressTime) ESP.restart();
  } else dualPressStart = 0;

  // Przewijanie i wybór urządzenia w skanerze
  if (!scannerDone && deviceCount > 0) {
    if (M5.BtnA.wasPressed()) selectedIndex = (selectedIndex + 1) % deviceCount;
    if (M5.BtnB.wasPressed()) {
      ADRES_OBD2 = devices[selectedIndex].mac;
      scannerDone = true;

      M5.Lcd.fillScreen(lightPurple);
      M5.Lcd.setCursor(4, 20);
      M5.Lcd.setTextSize(2);
      M5.Lcd.print("Wybrano:");
      M5.Lcd.setCursor(4, 40);
      M5.Lcd.print(devices[selectedIndex].name);
      M5.Lcd.setCursor(4, 60);
      M5.Lcd.print(ADRES_OBD2);
      delay(1000);

      if (SerialBT.connect(ADRES_OBD2)) {
        btConnected = true;
        initELM();
      }
    }

    M5.Lcd.fillScreen(lightPurple);
    M5.Lcd.setCursor(4, 8);
    M5.Lcd.setTextSize(2);
    M5.Lcd.print("Wybierz urzadzenie:");
    M5.Lcd.setCursor(4, 32);
    M5.Lcd.print(devices[selectedIndex].name);
  }

  // Wyświetlanie parametrów po wyborze urządzenia
  if (scannerDone && btConnected) {
    if (millis() - lastUpdate > updateInterval) {
      int value = readPID(pids[buttonIndex]);
      String label = labels[buttonIndex];

      M5.Lcd.fillScreen(lightPurple);
      M5.Lcd.setTextColor(WHITE);
      M5.Lcd.setTextSize(3);
      M5.Lcd.setCursor(10, 20);
      M5.Lcd.print(label);
      M5.Lcd.setCursor(10, 60);
      if (value >= 0) M5.Lcd.print(value);
      else M5.Lcd.print("---");

      lastUpdate = millis();
    }

    // Zmiana parametru przyciskiem A
    if (M5.BtnA.wasPressed()) {
      buttonIndex = (buttonIndex + 1) % numParams;
    }
  }
}
