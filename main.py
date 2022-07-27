import time
from machine import RTC
import urequests
import datalog_lib as dlog
import bmp180

print('sd', sd)

rtc = RTC()
now = rtc.datetime()
print('fecha:', now)
#t1 = time.ticks_ms()
#response = urequests.post("https://maker.ifttt.com/trigger/miguel/with/key/hITnIrHZrQUVdwBjyHkea3Q8I_IGzJRCTMCgPV-hW3o",
#        data = '{ "value1" : "a", "value2" : "b", "value3" : "c" } ')
#print(response.text)
#print('dt:', time.ticks_diff(time.ticks_ms(), t1))
#print(t1)
data ="---"+",---"*3
def web_page():
  global data
  now = rtc.datetime()
  date_str = []
  for d in now:
      date_str.append(str(d))

  header = [
          "Fecha",
          "Presión",
          "Temperatura (p)",
          "Viento (dir)",
          ]
  units =[
          "UTC",
          "mbar",
          "C",
          "º",
          ]

  html = """<html lang="es"><head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    #data_table{
        font-family: Arial, Helvetica, sans-serif;
        border-collapse: collapse;
        width: 100%:
    }

    #data_table td, #data_table th {
        border: 1px solid #ddd;
        padding: 8px;
    }

    #data_table tr:nth-child(even){background-color: #f2f2f2;}
    #data_table tr:hover {background-color: #ddd;}
    #data_table th{
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #5499C7;
        color: white;
    }
    </style>
  </head>
  <body><h1> Últimos datos recibidos:</h1>"""
  html += '<table id="data_table" >'
  html += '<tr> <th> Variable </th> <th> Valor</th> <th> Unidad</th></tr>'
  for i,d in enumerate(data.split(',')):
          html += '<tr> '
          html += '<td>'+header[i]+'</td>'
          html += '<td>'+d +'</td>'
          html += '<td>'+units[i] +'</td>'
          html += '</tr>'
  html += "</table></body></html>"
  return html

i2c = I2C(0, scl =Pin(22, Pin.OPEN_DRAIN), sda = Pin(21, Pin.OPEN_DRAIN) )
#configuración de socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
s.settimeout(0)
#canales analógicos
adc_wd = machine.ADC(Pin(33))
adc_wd.atten(machine.ADC.ATTN_11DB)

#conteo de pulsos 0
counter_p0=0
def call_p0(p):
    global counter_p0
    counter_p0 +=1
    print(p.value(), counter_p0, time.ticks_ms())

p0 = Pin(25, Pin.IN, Pin.PULL_UP)
p0.irq( call_p0,  trigger=Pin.IRQ_FALLING)

sample = False
def call_t0(t):
    global counter_p0
    global sample
    sample = True
    print('P0=', counter_p0)
#Configura timer 0 con el tiempo de muestreo
t0 = machine.Timer(0)
t0.init(period=2000, callback=call_t0)


while True:
    #print('aceptando conexión... ', end=' ')
    try:
        conn, addr = s.accept()
        #print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        #print('Content = %s' % str(request))
        response = web_page()
        conn.send(response)
        conn.close()
    except  (OSError):
        print('no se encontró conexión...', end= ' ')
    if sample == True:
        sample = False
        print("Tomando muestreo")
        #print('SD:', dlog.check_SD(sd))
        Tp, p =bmp180.pressure(i2c)
        now = rtc.datetime()
        wd = adc_wd.read()
        data = '{}/{:02}/{:02} {:02}:{:02}:{:02},{},{},{}'.format(
            now[0],
            now[1],
            now[2],
            now[4],
            now[5],
            now[6],
            p/100,
            Tp/10,
            360*wd/4095,
            )
        print(data)
