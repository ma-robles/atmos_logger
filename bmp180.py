"""
bmp180 library
"""
from ustruct import unpack
from time import sleep_ms

dir_bmp180 = 119
#read calibration data
def get_cal(i2c):
    cal_data = bytearray(22)
    i2c.readfrom_mem_into(dir_bmp180, 0xaa, cal_data)
    return unpack('>hhhHHHhhhhh', cal_data)

#wait conversion
def wait_conv(i2c):
    ctrl = bytearray(1)
    n =0
    i2c.readfrom_mem_into(dir_bmp180, 0xf4, ctrl)
    while ( ctrl[0] &(1<<5) != 0):
        sleep_ms(1)
        n+= 1
        if n == 60:
            return False
        i2c.readfrom_mem_into(dir_bmp180, 0xf4, ctrl)
    return True

#true pressure
#oss=0
def pressure(i2c):
    ctrl = bytes([0x2E])
    i2c.writeto_mem(119, 0xf4, ctrl)
    ut = bytearray(2)
    if wait_conv(i2c) == False:
        return 'NaN','NaN'
    i2c.readfrom_mem_into(dir_bmp180, 0xf6, ut)
    ctrl = bytes([0x34])
    i2c.writeto_mem(119, 0xf4, ctrl)
    UP = bytearray(2)
    UT = unpack('>H', ut)[0]
    AC1, AC2, AC3, AC4, AC5, AC6, B1, B2, MB,MC,MD = get_cal(i2c)
    X1 = ((UT-AC6)*AC5)>>15
    X2 = (MC<<11)//(X1 +MD)
    B5 = X1 + X2
    T = (B5 + 8) >> 4
    B6 = B5 - 4000
    X1 = (B2 * (B6*B6)>>12)>>11
    X2 = (AC2*B6)>>11
    X3 = X1 + X2
    B3 = (((AC1<<2) +X3) +2)>>2
    X1 = (AC3 *B6)>>13
    X2 = (B1 *((B6*B6)>>12))>>16
    X3 = (X1 +X2 +2)>>2
    B4 = (AC4*abs(X3 +32768))>>15
    if wait_conv(i2c) == False:
        return T,'NaN'
    i2c.readfrom_mem_into( dir_bmp180, 0xf6, UP)
    UP = unpack('>H', UP)[0]
    B7 = abs(UP -B3) *50000
    if (B7 < 0x80000000):
        p = (B7 <<1) //B4
    else:
        p = (B7//B4)<<1
    X1 =((p>>8)*(p>>8)*3038)>>16
    X2 =(-7357 *p) >>16
    return (T, p)
