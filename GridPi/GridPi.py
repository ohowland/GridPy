import json
from Modbus import Client
from time import sleep

if __name__ == '__main__':

    #TODO: base on local path.
    #sysconfig_path = '/home/pi/Public/GitHub/GridPi/bin/SysConfig.json'
    sysconfig_path = 'C:/Users/Owen/Git/GridPi/bin/SysConfig.json'

    with open(sysconfig_path, 'r') as outfile:
        sysconfig = json.loads(outfile.read())

    clients = list()

for client in sysconfig:
    clients.append(Client('Diesel1',sysconfig_path))
    clients.append(Client('BatteryInverter1',sysconfig_path))
    clients.append(Client('GridIntertie1',sysconfig_path))
    
    while True:
        for c in clients:
            for keys, values in c.cvt.items():
                print(c.process_name, keys, values)
        print('-------------------------')
        sleep(5)
