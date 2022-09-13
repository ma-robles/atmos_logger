import network
import usocket as socket
from machine import SDCard
from machine import I2C, Pin
from machine import RTC
import machine
import os
import time
import json
import bmp180
import datalog_lib as dlog
import ds3231
import sht75
from netinfo import *

i2c = I2C(0, scl =Pin(22, Pin.OPEN_DRAIN), sda = Pin(21, Pin.OPEN_DRAIN) )

sht_dat = Pin(26, Pin.OUT, Pin.PULL_UP)
sht_clk = Pin(27, Pin.OUT, Pin.PULL_UP)

wlan= dlog.wlan_connect( ssid, password )
if machine.reset_cause() != machine.DEEPSLEEP_RESET:
    if wlan.isconnected() == True:
        rtc = RTC()
        if dlog.get_date_NTP(['1.mx.pool.ntp.org', 'cronos.cenam.mx']):
            #(year, month, day, weekday, hours, minutes, seconds, subseconds)
            print('hora NTP:', rtc.datetime())
            print('hora ds:', ds3231.get_time(i2c))
            ds3231.set_time(i2c)
            print('hora ds actualizada:', ds3231.get_time(i2c))
        else:
            print('No NTP')
            print('hora:', rtc.datetime())
            YY, MM, DD,wday, hh, mm, ss, _ = ds3231.get_time(i2c)
            rtc.datetime( (YY, MM, DD, wday, hh, mm, ss, 0))
            print('DS:', rtc.datetime())
    else:
        print('No se pudo conectar!')
else:
    print('deep sleep!')
    print(path_SD)

wlan.active(False)

sd = SDCard( slot =2, freq =1000000)
os.mount(sd, '/sd')
    
print('SD files:')
print(os.listdir('/sd'))
os.umount('/sd')
print('desmontado')
#configuración de socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
s.settimeout(0)
#canales analógicos
adc_wd = machine.ADC(Pin(33))
adc_wd.atten(machine.ADC.ATTN_11DB)
adc_uv= machine.ADC(Pin(34))
adc_uv.atten(machine.ADC.ATTN_11DB)
adc_sun = machine.ADC(Pin(35))
adc_sun.atten(machine.ADC.ATTN_11DB)

#conteo de pulsos 0
counter_p0=0
def call_p0(p):
    global counter_p0
    counter_p0 +=1
    print(p.value(), counter_p0, time.ticks_ms())

p0 = Pin(25, Pin.IN, Pin.PULL_UP)
p0.irq( call_p0,  trigger=Pin.IRQ_FALLING)

