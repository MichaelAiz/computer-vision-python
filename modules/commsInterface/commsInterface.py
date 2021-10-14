import usb.core
import usb.util
import serial

class CommsInterface:
    def __init__(self, type: bool):
        """
        Initializes parameters for USB or UART

        Parameters
        ----------
        type: bool
            Boolean used to specify selection of USB or UART;
            0|False for USB, 1|True for UART
        """
        self.uart_or_usb = type
    
    def create_end_point_FC(self):
        """
        Issues a read command in either serial (UART) or pyusb (USB).
        EndpointId can be the specific serial port to use or the usb endpoint to be used. 
        """
        if self.uart_or_usb == 0:
            if self.idVendor and self.idProduct is not None:
                self.dev = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)
            else:
                self.dev = usb.core.find()
            if self.dev is None:
                raise ValueError('Device Not Found')

            self.ep = self.dev[0].interfaces()[0].endpoints()[0]
            self.dev.set_configuration()

            return self.ep.bEndpointAddress
        elif self.uart_or_usb == 1:
            return serial.Serial(self.uart_port, self.baudrate)

    def read(self, endpointId):
        """
        Issues a write command in either serial or pyusb.
        Data parameter should be a buffer. 
        """
        if self.uart_or_usb == 0:
            return self.dev.read(endpointId, self.ep.wMaxPacketSize)
        elif self.uart_or_usb == 1:
            read_data = endpointId.readline()
            return str(read_data[0:len(read_data)].decode('utf-8'))
        

    def write(self, endpointId, data):
        """
        Returns a new endpoint, either a Serial object (UART) or Endpoint object (USB), that points to our flightcontroller.
        """
        if self.uart_or_usb == 0:
            self.dev.write(endpointId, data)
            return True
        elif self.uart_or_usb == 1:
            endpointId.write(data.encode())
            endpointId.close()
            return True

class USBInterface(CommsInterface):
    def __init__(self, type: bool, idVendor=None, idProduct=None):
        self.idVendor = idVendor
        self.idProduct = idProduct
        super().__init__(self, type)

class UARTInterface(CommsInterface):
    def __init__(self, type: bool, uart_port, baudrate):
        self.uart_port = uart_port
        self.baudrate = baudrate
        super().__init__(self, type)


