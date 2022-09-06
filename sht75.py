from time import sleep_us
from time import sleep_ms
from machine import Pin
#sht_clk
#sht_dat
def get_T(sht_dat, sht_clk):
    reinicio_com( sht_dat, sht_clk)
    ini_trans(sht_dat, sht_clk)
    envia_byte(0b00000011,sht_dat, sht_clk);

def get_RH(sht_dat, sht_clk):
    reinicio_com(sht_dat, sht_clk)
    ini_trans(sht_dat, sht_clk)
    envia_byte(0b00000101,sht_dat, sht_clk)

def convert_trh( t, rh):
    d1 = -39.65
    d2 = 0.01
    c1 = -2.0468
    c2 = 0.0367
    c3 = -1.5955e-6
    t1 = 0.01
    t2 = 0.00008
    T = d1 + d2 *t
    RHl = c1 +c2*rh +c3*rh*rh
    RH = (T-25)*(t1+t2*rh)+RHl
    return T,RH

def trh(sht_dat, sht_clk):
    get_T(sht_dat, sht_clk)
    d1 = -39.65
    d2 = 0.01
    c1 = -2.0468
    c2 = 0.0367
    c3 = -1.5955e-6
    t1 = 0.01
    t2 = 0.00008
    t = lee_2bytes(sht_dat, sht_clk)
    get_RH(sht_dat, sht_clk)
    T = d1 + d2 *t
    rh = lee_2bytes(sht_dat, sht_clk)
    RHl = c1 +c2*rh +c3*rh*rh
    RH = (T-25)*(t1+t2*rh)+RHl
    return T,RH


def ini_trans(sht_dat, sht_clk):
    #Genera señal de inicio de transmisión
    sht_dat.on()
    sht_clk.off()
    sleep_us(2)
    sht_clk.on()
    sleep_us(1)
    sht_dat.off()
    sleep_us(1)
    sht_clk.off()
    sleep_us(2)
    sht_clk.on()
    sleep_us(1)
    sht_dat.on()
    sleep_us(1)
    sht_clk.off()

def reinicio_com(sht_dat, sht_clk):
    sht_clk.off()
    sht_dat.on()
    sleep_us(2)
    for i in range(9):
        sht_clk.on()
        sleep_us(2)
        sht_clk.off()
        sleep_us(2)
    ini_trans(sht_dat, sht_clk)
    
def bit_test(var_byte, n):
    return(1&(var_byte>>n))

def envia_byte(envia,sht_dat, sht_clk):
    sht_clk.off()
    for i in range(7,-1, -1):
        sht_dat.value(bit_test(envia, i))
        sleep_us(2)
        sht_clk.on()
        sleep_us(2)
        sht_clk.off()
    sht_dat.init(Pin.IN, Pin.PULL_UP)
    sleep_us(2)
    sht_clk.on()
    ack = sht_dat.value()
    sleep_us(2)
    sht_clk.off()
    sht_dat.init(Pin.OUT, Pin.PULL_UP)
    return ack

def lee_2bytes(sht_dat, sht_clk):
    sht_clk.off()
    sht_dat.init( Pin.IN, Pin.PULL_UP)
    # define el tiempo de espera
    # el máximo es 320ms para una medición de 14 bits
    # 400 ms
    ntry = 10 
    for i in range(ntry):
        if sht_dat.value() == 0:
            break
        sleep_ms(40)
    rcv = 0
    for i in range(15, -1, -1):
        sleep_us(2)
        sht_clk.on()
        sleep_us(1)
        bit_i = sht_dat.value()
        sleep_us(1)
        sht_clk.off()
        if bit_i == 1:
            rcv |= (1 << i)
        if i == 8:
            sht_dat.off()
            sleep_us(1)
            sht_clk.on()
            sleep_us(1)
            sht_clk
    sleep_us(2)
    sht_clk.on()
    sleep_us(2)
    sht_clk.off()
    sht_dat.init(Pin.OUT)
    return rcv

