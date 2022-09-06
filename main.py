import time
from machine import RTC
import urequests
import datalog_lib as dlog
import bmp180
import json

rtc = RTC()
now = rtc.datetime()
print('fecha:', now)
machine.freq(80000000)
print('CPU freq:', machine.freq()/1e6)
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
          "Temperatura",
          "Humedad rel",
          "Presión",
          "Temperatura (p)",
          "Viento (dir)",
          "UV",
          "Radiación",
          ]
  units =[
          "UTC",
          "C",
          "%",
          "mbar",
          "C",
          "º",
          "",
          "W/m2",
          ]

  html = """<!DOCTYPE html>
  <html lang="es"><head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="atmos_log.css">
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
    #print('P0=', counter_p0)
#Definición de intervalos
# Δs<=Δa<=Δi<=Δe
#muestreo en segundos
Δs = 2
#almacenamiento en minutos
Δa = 1
#envio dato instantáneo en minutos
Δi = 2
#envio archivo modificado en minutos
Δe = 20
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
time_sendi = norm_minute(time_now, Δi)
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
data['RH'] =0; units["RH"] = '%'
data['T'] =0; units["T"] = 'C'
data['P'] =0; units['P'] = "mbar"
data['Tp'] =0; units["Tp"] = 'C'
data['uv'] =0; units["uv"] = "index"
data['sun'] =0; units["sun"] = "W/m²"
#data['wd'] =0
wdt = machine.WDT(timeout =60000)
#data['ws'] =0
#Espera el minuto de almacenamiento siguiente
print('Esperando arranque:', end ='')
while time.mktime(time_now) < time.mktime(time_save):
    print('*', end='')
    time_now = time.gmtime()
    time.sleep(2)
    wdt.feed()
print('')
#Configura timer 0 con el tiempo de muestreo
t0 = machine.Timer(0)
t0.init(period=Δs*1000, callback=call_t0)

path_SD = '/sd'
filename_update ='files_update.json'
data_buffer = {}
timeout_send = 1.0
#separa url, asume que incluye puerto y protocolo
protoc, _, host = url_server.split('/',2)
host, port = host.split(':')
addr2 = socket.getaddrinfo(host, port)[0][-1]
print(addr2)
def cb_timeout(e):
    print('timeout error', )
    wdt.feed()
    raise OSError

while True:
    wdt.feed()
    wlan.active(False)
    time_now = time.gmtime()
    #Almacenamiento
    if time.mktime(time_now) >= add_minute(time_save, Δa):
        print('minuto:', time_save)

        #Procesa acumulados
        data = data_dic['data']
        data = data_mean(data, data_dic['ndata'])
        data_dic['id'] = ID
        data_str = '{}/{:02}/{:02} {:02}:{:02}:{:02}'.format(
                time_save[0],
                time_save[1],
                time_save[2],
                time_save[3],
                time_save[4],
                time_save[5],
                )
        data_dic['date'] = data_str
        for k in data.keys():
            data_str += ','+ str(data[k])
            print(k, data[k], sep=':', end=' ')
        print('')
        print('ndata:', data_dic['ndata'], end=' ', sep='')
        if dlog.check_SD(sd, path_SD) == True:
            #Almacena datos
            file_save = '{}_{}_{:02}_{:02}.csv'.format(
                    ID,
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
        #carga datos instantáneos en buffer
        data_buffer = data_dic.copy()
        data_buffer['data'] = data_dic['data'].copy()
        data = data_clean(data)
        data_dic['ndata'] = 0
        #actualiza time_save
        time_save = add_minute(time_save, Δa)
        time_save =time.gmtime(time_save)
        #print('buffer:', data_buffer)

    #envío de datos instantáneos
    if time.mktime(time_now) > time_sendi and data_buffer!={}:
        if wlan.isconnected() == False:
            wlan = dlog.wlan_connect(ssid, password)
        if wlan != None:
            data_json = json.dumps(data_buffer)+' '
            print('Enviando datos instantaneos a', host, data_buffer['data'])
            sock_send = socket.socket()
            sock_send.settimeout(timeout_send)
            try:
                sock_send.connect(addr2)
                print('connect')
                sock_send.send(bytes('PUT /insta HTTP/1.1\r\n', 'utf8'))
                sock_send.send(bytes('Content-Length: %s\r\n' % (len(data_json)+1), 'utf8'))
                sock_send.send(bytes('Content-Type: application/json\r\n\r\n', 'utf8'))
                sock_send.send(data_json)
                response = sock_send.recv(200)
                sock_send.close()
                if response.split()[1] == b'201':
                    print('datos instantáneos recibidos')
                else:
                    print(response)
            except OSError:
                print ('No hay conexión con el servidor ', host)
        else:
            print('No se pido conectar a WiFi')
        wlan.active(False)
        time_sendi = add_minute( time.gmtime(time_sendi), Δi)
        print('siguiente instantáneo:', time.gmtime(time_sendi))

    #envío de archivos de datos
    if time.mktime(time_now) > time_send:
        if wlan.isconnected() == False:
            wlan = dlog.wlan_connect(ssid, password)
        if wlan != None:
            fname_send = '/sd/{}_{}_{:02}_{:02}.csv'.format(
                    ID, time_now[0], time_now[1], time_now[2])
            print('Enviando archivo:', fname_send, end=',')
            if dlog.check_SD(sd) == True:
                fsize = os.stat(fname_send)
                print(fsize[6], "bytes")
                with open(fname_send, 'rb') as fsend:
                    sock_send = socket.socket()
                    sock_send.settimeout(timeout_send)
                    try:
                        sock_send.connect(addr2)
                        fname = fname_send.split('/')[-1]
                        sock_send.send(bytes('PUT /hist/%s HTTP/1.1\r\n' % (fname), 'utf8'))
                        sock_send.send(bytes('Content-Length: %s\r\n' % (fsize[6]), 'utf8'))
                        sock_send.send(bytes('Content-Type: text/csv\r\n\r\n', 'utf8'))
                        chunk_size = 1024
                        for chunk in range(0, fsize[6], chunk_size):
                            bdata =  fsend.read(min(chunk_size, fsize[6]-chunk))
                            sock_send.send( bdata)
                        response = sock_send.recv(200)
                        sock_send.close()

                        if response.split()[1] == b'200':
                            print('archivo recibido')
                        else:
                            print(response)
                    except OSError:
                        sock_send.close()
                        print('No hay conexión con servidor')
                os.umount('/sd')
            else:
                print('No hay memoria SD!')
        else:
            print('No se pido conectar a WiFi')
        wlan.active(False)
        time_send = add_minute( time.gmtime(time_send), Δe)
        print('siguiente archivo:', time.gmtime(time_send))

    if f_sample == True:
        start = time.ticks_ms()
        f_sample = False
        sht75.get_T(sht_dat, sht_clk)
        Tp, p =bmp180.pressure(i2c)
        t = sht75.lee_2bytes( sht_dat, sht_clk )
        sht75.get_RH(sht_dat, sht_clk)
        now = rtc.datetime()
        wd = adc_wd.read()
        uv = adc_uv.read()
        sun = adc_sun.read()
        rh = sht75.lee_2bytes( sht_dat, sht_clk )
        T, RH = sht75.convert_trh( t, rh)
        #acumulando
        data = data_dic['data']
        data_dic['ndata'] +=1
        data['P'] += p
        data['Tp'] += Tp
        data['uv'] += uv
        data['sun'] += sun
        data['RH'] += RH
        data['T'] += T
        #data['wd'] += wd
        #print('Δ1 =', time.ticks_diff(time.ticks_ms(), start))

        data_str ='{}/{:02}/{:02} {:02}:{:02}:{:02},'.format(
                now[0], now[1], now[2], now[4], now[5], now[6])
        data_str +='{:5.1f},{:3.0f},{:4.0f},{:5.1f},{:3.0f},{:2.0f},{:4.0f}'.format(
                T, RH, p/100, Tp/10, 360*wd/4095, uv, sun,)
        #print(data_str)
        #print('Δ2 =', time.ticks_diff(time.ticks_ms(), start))

    time.sleep_ms(500)
    continue
    #atendiendo llamadas al servidor interno
    #print('aceptando conexión... ', end=' ')
    if wlan.isconnected() == False:
        wlan = dlog.wlan_connect(ssid, password)
    if wlan == None:
        continue
    try:
        conn, addr = s.accept()
        #print('Got a connection from %s' % str(addr))
        request = str(conn.recv(1024))
        #print('Content = %s' % str(request))
    except  (OSError):
        #print('*', end= ' ')
        continue
    req_pos = request.find("atmos_log.css")
    print('css pos:', req_pos)
    if req_pos!= -1:
        file_send = '/atmos_log.css'
        fsize = os.stat(file_send)
        print( fsize)
        conn.send('HTTP/1.1 200 OK\r\n')
        conn.send('Content_Lenght: '+str(fsize[6])+'\r\n')
        conn.send('Content-Type: text/css\r\n\r\n')
        with open(file_send) as file:
            for line in file:
                conn.send(line)
            conn.send('\r\n')
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
                    conn.send('Content-Disposition: attachment; filename= /%s\r\n' % req_dic['get_csv'])
                    conn.send('Content-Type: text/csv\r\n\r\n')
                with open(file_send) as file:
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
