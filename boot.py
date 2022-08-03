import network
from time import sleep
import usocket as socket
from machine import SDCard
from machine import I2C, Pin
from machine import RTC
import machine
import os
import datalog_lib as dlog
import ds3231

# punto de acceso
#ap= network.WLAN(network.AP_IF)
#ap.active(True)
#ap.config(essid='esp32', password='testesp32' )
#print(ap.ifconfig())

ssid = "TP-Link_A782"
password = "00196215"
wlan= dlog.wlan_connect( ssid, password )
print(wlan.ifconfig())

i2c = I2C(0, scl =Pin(22, Pin.OPEN_DRAIN), sda = Pin(21, Pin.OPEN_DRAIN) )
print("I2C encontradas:", i2c.scan())

rtc = RTC()
if dlog.get_date_NTP(['1.mx.pool.ntp.org', 'cronos.cenam.mx']):
    #(year, month, day, weekday, hours, minutes, seconds, subseconds)
    print('hora NTP:', rtc.datetime())
    print('hora ds:', ds3231.get_time(i2c))
    ds3231.set_time(i2c)
    print('hora ds:', ds3231.get_time(i2c))
else:
    print('No NTP')
    print('hora:', rtc.datetime())
    YY, MM, DD,wday, hh, mm, ss, _ = ds3231.get_time(i2c)
    rtc.datetime( (YY, MM, DD, wday, hh, mm, ss, 0))
    print('DS:', rtc.datetime())


sd = SDCard( slot =2, freq =1000000)
os.mount(sd, '/sd')
print(os.listdir())
with open('/sd/test.txt', 'w') as file:
    file.write('texto de prueba\n')
    
print('files:')
print(os.listdir('/sd'))
os.umount('/sd')
print('desmontado')

os.mount(sd, '/sd')
print('montado')
with open('/sd/test.txt') as file:
    for row in file:
        print(row)

os.umount('/sd')