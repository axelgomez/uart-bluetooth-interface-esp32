import time
import machine
from main import UartBLE

def cada1SegundoEnviar(taximetro, texto, led=True):
    led = machine.Pin(25, machine.Pin.OUT) # LED on the board
    i = 0
    while True:
        taximetro.enviar_dato(dato='{}{}'.format(texto,i),notify=True)
        i+=1
        if led.value() == 0:
            led.value(1)
        else:
            led.value(0)
        if (i > 50):
            i = 0
        time.sleep(1)