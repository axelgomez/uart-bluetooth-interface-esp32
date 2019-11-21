import time
import machine
from main import UartBLE

def cada1SegundoEnviar(taximetro, texto, led=True):
    led = machine.Pin(25, machine.Pin.OUT) # LED on the board
    i = 0
    while True:
        status=taximetro.leer_uart()
        if(status == True):
            taximetro.enviar_dato_uart()
        elif (status == -1):
            pass
            #print("no hay datos para recibir por UART, status: {}".format(status))
        elif (status == -2):
            print("fallo la recepcion de los datos por UART, status: {}".format(status))
            taximetro.limpiar_buf_uart()
        i+=1
        if led.value() == 0:
            led.value(1)
        else:
            led.value(0)
        if (i > 50):
            i = 0
        time.sleep(1)