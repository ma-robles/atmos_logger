import time
from machine import RTC
import urequests
import datalog_lib as dlog
import bmp180
import json

print('sd', sd)

rtc = RTC()
now = rtc.datetime()
print('fecha:', now)
#t1 = time.ticks_ms()
#print('dt:', time.ticks_diff(time.ticks_ms(), t1))
#print(t1)
data_str ="---"+",---"*3
def web_page():
  global data_str
  now = rtc.datetime()
  date_str = []
  for d in now:
      date_str.append(str(d))

  header = [
          "Fecha",
          "Presión",
          "Temperatura (p)",
          "Viento (dir)",
          "UV",
          "Radiación",
          ]
  units =[
          "UTC",
          "mbar",
          "C",
          "º",
          "",
          "W/m2",
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
  for i,d in enumerate(data_str.split(',')):
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

f_sample = False
def call_t0(t):
    global counter_p0
    global f_sample
    f_sample = True
    print('P0=', counter_p0)
#Definición de intervalos
# Δs<=Δa<=Δi<=Δe
#muestreo en segundos
Δs = 2
#almacenamiento en minutos
Δa = 1
#envio dato instantáneo en minutos
Δi = 10
#envio archivo modificado en minutos
Δe = 10
#sincronización hora NTP en horas
Δn = 6

#normaliza minuto de inicio con respecto a la hora
def norm_minute(time_now, δmin):
    time_new = list(time_now)
    time_new[4] = (time_now[4]//δmin)*δmin
    time_new[5] =0
    time_new = time.mktime(time_new) +δmin*60
    return time_new

#agrega δmin minutos a la hora dada en time_now
def add_minute(time_now, δmin):
    time_new = list(time_now)
    time_new[5] =0
    time_new = time.mktime(time_new) +δmin*60
    return time_new

time_now = time.gmtime()
print('actual:', time_now)
time_save =norm_minute(time_now, Δa)
time_save =time.gmtime(time_save)
print('save:', time_save)
time_sendi = norm_minute(time_now, Δe)
print('sendi:', time.gmtime(time_sendi))
time_send = norm_minute(time_now, Δe)
print('send:', time.gmtime(time_send))

def data_clean(data):
    for k in data.keys():
        data[k] =0
    return data
def data_mean(data, ndata):
    for k in data.keys():
        data[k]/=ndata
    return data
data_dic = {}
data_dic['ndata']=0
data_dic['data'] = {}
data_dic['units'] = {}
data = data_dic['data']
units = data_dic['units']
data['P'] =0; units['P'] = "mbar"
data['Tp'] =0; units["Tp"] = 'C'
data['uv'] =0; units["uv"] = "index"
data['sun'] =0; units["sun"] = "W/m²"
#data['wd'] =0
#data['ws'] =0
#Espera el minuto de almacenamiento siguiente
print('Esperando arranque:', end ='')
while time.mktime(time_now) < time.mktime(time_save):
    print('*', end='')
    time_now = time.gmtime()
    time.sleep(1)
print('')
#Configura timer 0 con el tiempo de muestreo
t0 = machine.Timer(0)
t0.init(period=Δs*1000, callback=call_t0)

path_SD = '/sd'
filename_update ='files_update.json'
wdt = machine.WDT(timeout =5000)
while True:
    wdt.feed()
    time_now = time.gmtime()
    #Almacenamiento
    if time.mktime(time_now) >= add_minute(time_save, Δa):
        print('minuto:', time_save)

        #Procesa acumulados
        data = data_dic['data']
        data = data_mean(data, data_dic['ndata'])

        data_str = '{}/{:02}/{:02} {:02}:{:02}:{:02}'.format(
                time_save[0],
                time_save[1],
                time_save[2],
                time_save[3],
                time_save[4],
                time_save[5],
                )
        for k in data.keys():
            data_str += ','+ str(data[k])
            print(k, data[k], sep=':', end=' ')
        print('')
        print('ndata:', data_dic['ndata'], end=' ', sep='')
        if dlog.check_SD(sd, path_SD) == True:
            #Almacena datos
            file_save = '{}_{:02}_{:02}.csv'.format(
                    time_save[0],
                    time_save[1],
                    time_save[2],
                    )
            print(os.listdir( path_SD ))
            #Actualiza lista de archivos modificados
            path_save  = path_SD +'/' +file_save
            path_update = path_SD +'/' +filename_update
            with open(path_save, 'a') as file:
                file.write(data_str +'\n')
            try:
                with open(path_update) as jsfile:
                    list_update = json.load(jsfile)
            except:
                list_update = []
            if not path_save in list_update:
                list_update.append(path_save)
            with open(path_update, 'w') as jsfile:
                json.dump(list_update, jsfile)
            os.umount( path_SD )
            print('modificados:', list_update)
        else:
            print('No hay memoria SD!!!')
        data_json = json.dumps(data_dic)+' '
        print(data_json)
        response = urequests.request("PUT", "http://192.168.50.254:8080/echo",
                headers = {'content-type': 'application/json'},
                data = data_json,
            )
        print(response.text)
        data = data_clean(data)
        data_dic['ndata'] = 0
        #actualiza time_save
        time_save = add_minute(time_save, Δa)
        time_save =time.gmtime(time_save)

    if f_sample == True:
        f_sample = False
        Tp, p =bmp180.pressure(i2c)
        now = rtc.datetime()
        wd = adc_wd.read()
        uv = adc_uv.read()
        sun = adc_sun.read()
        #acumulando
        data = data_dic['data']
        data_dic['ndata'] +=1
        data['P'] += p
        data['Tp'] += Tp
        data['uv'] += uv
        data['sun'] += sun
        #data['wd'] += wd

        data_str = '{}/{:02}/{:02} {:02}:{:02}:{:02},{},{},{},{},{}'.format(
            now[0],
            now[1],
            now[2],
            now[4],
            now[5],
            now[6],
            p/100,
            Tp/10,
            360*wd/4095,
            uv,
            sun,
            )
        print(data_str)
        print('acumulados:', end=' ')
        for k in data.keys():
            print(k, data[k], sep=':', end =' ')
        print('')

    if time.mktime(time_now) >= time_send:
        print('')
        time_send = norm_minute( time_now, Δe)
        print('send:', time_send)
    #print('aceptando conexión... ', end=' ')
    try:
        conn, addr = s.accept()
        #print('Got a connection from %s' % str(addr))
        request = str(conn.recv(1024))
        #print('Content = %s' % str(request))
    except  (OSError):
        #print('*', end= ' ')
        continue
    req_pos = request.find('/atmlog?')
    print(request)
    if req_pos == 6:
        req_info = request.split()[1]
        req_dic = {}
        for info in req_info[8:].split('&'):
            try:
                info_k, info_val = info.split('=')
                req_dic[info_k] = info_val
            except:
                pass
        flag_view = False
        if "view" in req_dic:
            if req_dic["view"] == "TRUE":
                flag_view = True
        if "get_csv" in req_dic:
            file_send = '/sd/'+req_dic['get_csv']
            print('file:', file_send, end=' ')
            if dlog.check_SD(sd) == True:
                fsize = os.stat(file_send)
                print( fsize)
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content_Lenght: '+str(fsize[6])+'\r\n')
                if flag_view==True:
                    conn.send('Content-Disposition: inline\r\n')
                    conn.send('Content-Type: text/txt\r\n\r\n')
                else:
                    conn.send('Content-Disposition: attachment; filename="data.csv"\r\n')
                    conn.send('Content-Type: text/csv\r\n\r\n')
                with open('/sd/test.txt') as file:
                    for line in file:
                        conn.send(line)
                    conn.send('\r\n')
                os.umount('/sd')
            else:
                print('No hay memoria SD!!!')
                conn.send('HTTP/1.1 404 Not Found\r\n')
    else:
        response = web_page()
        conn.send(response)
    conn.close()
