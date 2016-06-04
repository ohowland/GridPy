from ModbusServer import Client
from time import sleep
from threading import Thread

if __name__ == '__main__':

    sysconfig_path = '/home/pi/Public/GitHub/GridPi/bin/SysConfig.json'
    
    clients = list()

    clients.append(Client('Diesel1',sysconfig_path))
    clients.append(Client('BatteryInverter1',sysconfig_path))
    clients.append(Client('GridIntertie1',sysconfig_path))
    
    while True:
        
        for c in clients:
            for i in range(0,len(c.reg)):
                print(c.processname, c.reg[i]['name'],':',c.reg[i]['value'])
        print('-----------------------------')
        sleep(5)
