#usando Peripheral Role (GATT Server)
#DOCU: http://docs.micropython.org/en/latest/library/ubluetooth.html
import bluetooth
import struct
import time
import machine

from micropython import const
_IRQ_CENTRAL_CONNECT                 = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT              = const(1 << 1)

_UART_TX = (
    bluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E'),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E'),
    bluetooth.FLAG_WRITE,
)
_UART_SERVICE= (
    bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E'),
    (_UART_TX, _UART_RX),
)

class UartBLE:
    def __init__(self, ble, name='axelukan'):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        ( (self._tx, self._rx,), ) = self._ble.gatts_register_services((_UART_SERVICE,))
        print("tx: {}, rx:{}".format(self._tx, self._rx))
        #((self._handle,),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        #self._payload = bytearray('\x02\x01\x02') + self.adv_encode_name('axelukan')
        self._payload = bytearray('\x02\x01\x02') + bytearray((len(bytes('Axelukan', 'ascii')) + 1, 0x09)) + bytes('Axelukan', 'ascii')
        print("payload:{}".format(self._payload))
        self._advertise()
    def _irq(self, event, data):
        # Trackear conexiones para que podamos enviar notificaciones
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _, = data
            self._connections.remove(conn_handle)
            # Empezar a advertisear nuevamente para permitir una nueva conexion
            self._advertise()
    def _advertise(self, interval_us=500000):
        #self._ble.gap_advertise(interval_us, adv_data=self._payload)
        #self._ble.gap_advertise(0, bytearray('\x02\x01\x02') + self.adv_encode_name('Axelukan'))
        self._ble.gap_advertise(interval_us, adv_data=self._payload)
        print("advertise")
    def adv_encode_name(name):
        name = bytes(name, 'ascii')
        return bytearray((len(name) + 1, 0x09)) + name
    def enviar_dato(self, dato, notify=False):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        # Write the local value, ready for a central to read.
        dato_binario = struct.pack("<%us" % (len(dato)+2), "{}\r\n".format(dato))
        print("se tratara de enviar dato a {} con {}".format(self._tx,dato_binario))
        self._ble.gatts_write(self._tx, dato_binario)
        if notify:
            for conn_handle in self._connections:
                # Notify connected centrals to issue a read.
                print("se notificara a {} . {} con {}".format(conn_handle, self._tx, dato_binario))
                self._ble.gatts_notify(conn_handle, self._tx, dato_binario)

def demo1():
    bt = bluetooth.BLE()
    taximetro = UartBLE(bt)
    i = 0
    while True:
        taximetro.enviar_dato(dato='hola{}'.format(i),notify=True)
        i+=1
        if (i > 50):
            i = 0
        time.sleep(1)

def demo2(): #FUNCIONA OK CON USB PERO NO CON ALIMENTACION EXTERNA
    from main import UartBLE
    from test import cada1SegundoEnviar

    bt = bluetooth.BLE()
    taximetro = UartBLE(bt)
    cada1SegundoEnviar(taximetro,'texto')

def demo3(): #FUNCIONA OK CON ALIMENTACION EXTERNA DESDE EL RELOJ Y LED A 5V
    led = machine.Pin(25, machine.Pin.OUT) # LED on the board
    while True:
        if led.value() == 0:
            led.value(1)
        else:
            led.value(0)
        time.sleep(1)

def demo4(): #FUNCIONA OK CON ALIMENTACION EXTERNA DESDE EL RELOJ Y LED A 5V
    from main import UartBLE
    from test import cada1SegundoEnviar

    bt = bluetooth.BLE()
    taximetro = UartBLE(bt)
    cada1SegundoEnviar(taximetro=taximetro,texto='texto',led=True)


if __name__ == '__main__':
    demo4()



#bt.active(1)
#def bt_irq(event, data):
#    print(event, data)
#bt.irq(bt_irq)



#
##bt.gap_advertise(0, bytearray('\x02\x01\x02') + adv_encode_name('Axelukan'))
#
#( (tx, rx,), ) = bt.gatts_register_services((UART_SERVICE,))
##Los handles (tx, rx) pueden ser usador con gatts_read, gatts_write y gatts_notify segun corresponda
#
### detecte un problema que si hago de advertise, quiero dejar de advertisear
### y no se me conecta nadie, nunca puede dejar de advertisear
### el workaround puede llegar a ser resetear el micro...
#
#dato = bt.gap_advertise(100, bytearray('\x02\x01\x02') + adv_encode_name('Axelukan'))
##'''
##1 (0, 1, b'Q\xcb\xcf\xfec\xef')
##'''
#
##guardamos dato para luego notificar
#dato = (0, 1, b'Q\xcb\xcf\xfec\xef')
#conn_handle, _, _, = dato
##enviamos data para luego notificar
#x = 'Como vaaaa'
#dato_binario = struct.pack("<%us" % (len(x)+2), "{}\r\n".format(x))
#bt.gatts_write(tx, dato_binario)
#
#bt.gatts_notify(conn_handle,tx,dato_binario)
##JOYAAAA
##Si y solo si notifico a la aplicación, me toma el valor cambiado y lo muestra en el terminal
#

