# benötigte Bibliotheken und Module importieren:

from machine import Pin, I2C, Timer, RTC
from imu import MPU6050
import time
import network
import files
import ntptime
import socket

files # alle Dateien ausgeben, die auf dem Mikrocontroller gespeichert sind


# benötigte Funktionen definieren:

# Funktion current_time() definieren - definiert aktuelle Zeit:

def current_time():
    dt = RTC().datetime()
    dt = dt[:3] + dt[4:]
    return dt


# Funktion wifi_connect definieren - stellt WLAN-Verbindung her:

def wifi_connect():
    print("Stelle Verbindung zu WLAN her.")
    WIFI_SSID = "Laras iPhone(3)"
    WIFI_PW = "11223XXX"
    
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PW)
        while not wlan.isconnected():
            pass
    print("VERBUNDEN:", WIFI_SSID)
    time.sleep(1)
    ntptime.settime()


# Funktion read_imu definieren - liest die Daten vom Beschleunigungssensor aus sendet diese über eine TCP-Verbindung:

def read_imu(tim):
    try:
        global DataCounter
        global accel
        if DataCounter == 0:
            dt = current_time()
            timestamp = str(dt[0]) + "," + str(dt[1]) + "," + str(dt[2]) + "," + str(dt[3]) + "," + str(dt[4]) + "," + str(
                dt[5]) + "," + str(dt[6]) + ")"
            TCP_socket.send(timestamp.encode())
        TCP_socket.send(str(accel.xyz).encode())
        DataCounter = DataCounter + 1
        if DataCounter == 200:
            DataCounter = 0
    except OSError:
        tim.deinit()
        print("TCP-Verbindung abgebrochen. Mikrocontroller herunterfahren.")
        TCP_socket.close()


# Zuvor definierte Funktionen aufrufen um Verbindung herzustellen:
# benötigte Variablen definieren:

wifi_connect()
DataCounter = 0
TCP_IP = '192.168.0.155'
TCP_PORT = 8000
BUFFER_SIZE = 15000
connection_status = False

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
mpu6050 = MPU6050(i2c)
accel = mpu6050.accel
tim = Timer(-1)

while not connection_status:
    print("Verbindung über TCP herstellen... ")
    try:
        TCP_socket = socket.socket()
        print(TCP_socket)
        addrinfos = socket.getaddrinfo(TCP_IP, TCP_PORT)
        print(addrinfos)
        TCP_socket.connect(addrinfos[0][4])
        connection_status = True
        print("TCP-Verbindung hergestellt. Messung starten.")
    
    except OSError:
        print("Verbindung fehlgeschlagen. Bitte warten... ")
        time.sleep(2)
tim.init(period=10, mode=Timer.PERIODIC, callback=read_imu)
