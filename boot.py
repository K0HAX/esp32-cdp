import sys
import time
import w5500
from machine_i2c_adafruit_lcd import I2cLcd
import machine
import cdp
import json
import re
import _thread

def initDisplay(sda=machine.Pin(21), scl=machine.Pin(22), freq=50000):
    DEFAULT_I2C_ADDR = 0x20
    i2c = machine.SoftI2C(sda=sda, scl=scl, freq=freq)
    display = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)
    display.clear()
    display.move_to(0, 0)
    return display

def getFrame(socket_num):
    while 1:
        try:
            data = wiz.frame_dump(socket_num)
            if data:
                break
        except Exception as e:
            sys.print_exception(e)
    return data

def scrollText(display, speed, line1):
    clearLine = ' ' * display.num_columns
    display.move_to(0, 0)
    display.putstr(clearLine)
    msg = line1
    while True:
        for i in range(len(msg)):
            len2 = min(display.num_columns, len(line1) - i)
            len1 = display.num_columns - len2
            msg2 = ''
            if len2 > 0:
                msg2 += msg[i:i+len2]
            if len1 > 0:
                msg2 += msg[0:len1]
            display.move_to(0, 0)
            display.putstr(msg2)
            time.sleep_ms(speed)

display = initDisplay()
display.putstr("Initializing")
time.sleep(2)
wiz = w5500.w5500(debug=False)
mSock = wiz.get_socket()
display.clear()
display.move_to(0, 0)
display.putstr("Opening socket")
time.sleep(1)
display.putstr(".")
time.sleep(1)
display.putstr(".")
mListen = wiz.socket_open(mSock, conn_mode=w5500.SNMR_MACRAW)
display.clear()
display.move_to(0, 0)
display.putstr("Waiting for data")
haveCDP = False
i = 0
display.move_to(0, 1)
display.putstr("Attempt ".format(i))
while haveCDP == False:
    display.move_to(8, 1)
    display.putstr("{}".format(i))
    if i >= 9:
        machine.reset()
    data = getFrame(mSock)
    haveCDP = cdp.getPacketType(data['unknown'])
    print(haveCDP)
    i += 1
print(json.dumps(data))
cdpVersion = cdp.getCdpVersion(data['unknown'])
cdpData = []
srcMac = "".join(x for x in data['srcmac'])
if cdpVersion == 2:
    display.clear()
    display.move_to(0, 0)
    display.putstr("CDP v2")
    display.move_to(0, 1)
    display.putstr(srcMac)
    time.sleep(2)
    cdpData = cdp.CDPv2(data['unknown'])
elif cdpVersion == 1:
    display.clear()
    display.move_to(0, 0)
    display.putstr("CDP v1")
    display.move_to(0, 1)
    display.putstr(srcMac)
    time.sleep(2)
    cdpData = cdp.CDPv1(data['unknown'])
print(json.dumps(cdpData))
display.clear()
display.move_to(0, 0)
cdpParsed = { 'Device ID': None, 'Port ID': None, 'IP Address': None }
for attribute in cdpData:
    if attribute['type'] == 'Device ID':
        cdpParsed['Device ID'] = attribute['data'].split('.')[0]
    if attribute['type'] == 'Port ID':
        cdpParsed['Port ID'] = attribute['data']
    if attribute['type'] == 'IP Address':
        cdpParsed['IP Address'] = attribute['address']
#device_id = (cdpParsed['Device ID'][0:15] + '..') if len(cdpParsed['Device ID']) > 17 else cdpParsed['Device ID']
device_id = cdpParsed['Device ID']
pattern = r'^([A-Z][a-z])[A-Za-z]+'
port_id = re.sub(pattern, r'\1', cdpParsed['Port ID'])
display.move_to(0, 1)
display.putstr("{}".format(port_id))
scrollArgs = (display, 750, "{} | ".format(device_id))
myScrollThread = _thread.start_new_thread(scrollText, scrollArgs)
#display.putstr("{}".format(device_id))
#def scrollText(display, speed, line1):

