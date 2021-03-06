import bluetooth
import serial
from numpy import nanmean

MODE_WIRED = 0
MODE_WIRELESS = 1


class ImuSensor:
    def __init__(self, mode, name):
        self.__sens_acc = 2048
        self.__sens_gyro = 16.4
        self.__mode = mode
        if mode is MODE_WIRED:
            self.serial_sensor = serial.Serial(name)
        elif mode is MODE_WIRELESS:
            devices = bluetooth.discover_devices(lookup_names=True)
            sensor_device = None
            for device in devices:
                if device[1] == name:
                    sensor_device = device
            if sensor_device is None:
                raise RuntimeError('Bluetooth sensor could not be found.')
            services = bluetooth.find_service(address=sensor_device[0])
            for serv in services:
                if serv['name'] == b'ESP32SPP\x00':
                    self.bt_sensor = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    self.bt_sensor.connect((serv['host'], serv['port']))
                    self.bt_sensor.setblocking(0)
                    self.bt_sensor.settimeout(1000)
                    return
            raise RuntimeError('Could connect to sensor.')
        else:
            raise ValueError('Invalid mode selected.')

    def __del__(self):
        if hasattr(self, 'serial_sensor'):
            self.serial_sensor.close()
        elif hasattr(self, 'bt_sensor'):
            self.bt_sensor.close()

    def __read(self, byte_len):
        if self.__mode is MODE_WIRED:
            return self.serial_sensor.read(byte_len)
        elif self.__mode is MODE_WIRELESS:
            return self.bt_sensor.recv(byte_len)

    def __write(self, data):
        if self.__mode is MODE_WIRED:
            return self.serial_sensor.write(data)
        elif self.__mode is MODE_WIRELESS:
            return self.bt_sensor.send(data)

    def __convert_acc(self, data):
        return data/self.__sens_acc

    def __convert_gyro(self, data):
        return data/self.__sens_gyro

    def take_measurement(self):
        self.__write(b'a\n')
        inbytes = b''
        inbyte = [inbytes] * 6
        output = [None] * 6
        while len(inbytes) < 12:
            inbytes += self.__read(12 - len(inbytes))
        for z in range(0, 6):
            input_bytes = inbytes[z*2:z*2+2]
            num = int.from_bytes(input_bytes, "big", signed=True)
            if z < 3:
                output[z] = self.__convert_acc(num)
            else:
                output[z] = self.__convert_gyro(num)
        return output
