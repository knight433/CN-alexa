import socket
import time 
from threading import Timer
from gpiozero import LED

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind = (('',5000))
s.listen(5)
print('server is now running')
clientsocket,address=s.accept()
global led
led = LED(17)

def runpin(data):
    if data == 'on':
        print('led on')
        led.on()
    elif data == 'off':
        print('turning off the led')
        led.off()

while True:
    data = clientsocket.recv(1024.decode('utf-8'))

    if not data:
        print('closed')
        break

    runpin(data)

clientsocket.close()
s.close()