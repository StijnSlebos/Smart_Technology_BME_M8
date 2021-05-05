import bluetooth  # import bluetooth libary for communication with the esp32
from numpy import nanmean  # import numpy to calculate mean for moving average

print("Scanning...")
devices = bluetooth.discover_devices(lookup_names=True)  # searches for bluetooth devices
print(devices)
filter_list = [[] for _ in range(6)]  # creates list for moving average
wirelessIMUs = []
sensitivity_acc = 2048
sensitivity_gyro = 16.4

for device in devices:
    if device[1] == 'WirelessIMU-A' or device[1] == 'WirelessIMU-B':  # searches for a device called: WirelessIMUX. in which X is the number on your casing
        wirelessIMUs.append(device)

print("Found these devices: ", wirelessIMUs)

IMUservices = []

for addr, name in wirelessIMUs:  # if correct devices are found add them to the list for connection
    print("Connecting to: ", addr)
    services = bluetooth.find_service(address=addr)
    for serv in services:
        if serv['name'] == b'ESP32SPP\x00':
            IMUservices.append(serv)

sensors = []

for IMU in IMUservices:  # initialize the IMU's as sensors
    sensor = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sensor.connect((IMU['host'], IMU['port']))
    sensor.setblocking(0)
    sensor.settimeout(1000)
    sensors.append(sensor)

output = [None] * 6  # Create list to store data
output_real = [None] * 6

for sensor in sensors:
    sensor.send('a')


def moving_average(input, k):  # moving average function !!for one sensor only now!!  returns the moving average of the data
    filter_list[k].append(input)  # add new value to the list
    if (len(filter_list[
                k]) >= 2):  # if list is larger then N remove the oldest data point, N determines the size of your list for the moving average
        filter_list[k].pop(0)
    final = nanmean(filter_list[k])  # Calculate the mean of the list
    return final  # Return mean


def real_numbers(input, k):  # real numbers function transfers into actual values
    if k <= 2:  # first 3 are acc data so divide by that sensitivity
        converted = input / sensitivity_acc
    if k >= 3:  # Last 3 are gyro data so divide by that sensitivity
        converted = input / sensitivity_gyro
    return converted  # returns converted value


while True:

    for sensor in sensors:
        inbytes = b''
        inbyte = [inbytes] * 6
        while len(inbytes) < 12:
            inbytes += sensor.recv(12 - len(inbytes))  # Collects data from sensor in bytes
        for z in range(0, 6):
            inbyte[z] += inbytes[z * 2:z * 2 + 2]
            inbyte[z] = int.from_bytes(inbyte[z], "big", signed="True")  # converts from bytes to int
            output[z] = moving_average(inbyte[z], z)  # Calls moving average function
            output_real[z] = real_numbers(output[z], z)  # calls real_numbers function
        sensor.send('a')
        print(sensor, output_real)
        #print(int.from_bytes(inbytes[6:8], "big", signed="True"))  # prints output
