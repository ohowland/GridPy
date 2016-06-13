from ModbusServer import Client
from time import sleep
import threading

if __name__ == '__main__':

    jobs = list()
    clients = list()
    clients[0] = Client('C:/Users/Owen/Git/GridPi/bin/Diesel.json')
    clients[1] = Client('C:/Users/Owen/Git/GridPi/bin/BattInv.json')

    for c in clients:
        c.init_connection()
        thread = threading.Thread(target=c.read())
        jobs.append(thread)

    while True:

        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        print('update complete')

    for c in clients:
        print(c.get('kW'))
        print(c.get('kVAR'))
    sleep(5)
