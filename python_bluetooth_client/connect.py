import bluetooth
import time
import matplotlib.pyplot as plt  # libary to plot
from scipy.ndimage.filters import uniform_filter1d  # moving average filter

print("Scanning...")
devices = bluetooth.discover_devices(lookup_names=True)
print(devices)
N = 50
readings = arr = [[] for _ in range(6)]
IMU_data = [[] for _ in range(6)]
x_co_gy = 0

wirelessIMUs = []
for device in devices:
    if device[1] == 'WirelessIMU4':
        wirelessIMUs.append(device)

print("Found these devices: ", wirelessIMUs)

IMUservices = []

for addr, name in wirelessIMUs:
    print("Connecting to: ", addr)
    services = bluetooth.find_service(address=addr)
    for serv in services:
        if serv['name'] == b'ESP32SPP\x00':
            IMUservices.append(serv)

sensors = []

for IMU in IMUservices:
    sensor = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sensor.connect((IMU['host'], IMU['port']))
    sensor.setblocking(0)
    sensor.settimeout(1000)
    sensors.append(sensor)

start = time.time()

output = [None] * 6

for sensor in sensors:
    sensor.send('a')


#def my_filter(x):  # movingaverage filter + plots
    #x_co_gy = uniform_filter1d(x, size=N)
    #y_co = uniform_filter1d(y, size=N)
    #z_co = uniform_filter1d(z, size=N)
    #my_plot(x, x_co_gy, 'x_co')
    #my_plot(y, y_co, 'y_co')
    #my_plot(z, z_co, 'z_co')
def my_plot(x_1, y_1, title):  # create the plots
    plt.plot(x_1)
    plt.plot(y_1)
    plt.xlabel(title)
    plt.show()

def my_3dplot(xs, ys, zs):  # create 3d plots with all the data
    fig = plt.figure()
    ax = plt.axes(projection="3d")
    ax.plot3D(xs, ys, zs)
    plt.show()

for i in range(1000):
    for sensor in sensors:
        inbytes = b''
        while len(inbytes)<12:
            inbytes+=sensor.recv(12-len(inbytes))
        sensor.send('a')
        #input = sensor.recv(12)
        for j in range(0, 12, 2):
            output[int(j/2)] = inbytes[j] << 8 | inbytes[j + 1]
        for k in range(6):
            readings[k].append(output[k])
            IMU_data[k] = uniform_filter1d(readings[k], size=N)
            print(output)



end = time.time()
avg = (end - start) / 1000
f = 1 / avg
print('frequency: %f' % f)

for i in range(6):
    my_plot(readings[i], IMU_data[i], 'x_co')

#my_3dplot(IMU_data[0], IMU_data[1], IMU_data[2])
my_3dplot(IMU_data[3], IMU_data[4], IMU_data[5])
