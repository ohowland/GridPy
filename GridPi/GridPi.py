import json
import os
from Modbus import Client
from time import sleep

if __name__ == '__main__':

    sysconfig_path = os.path.join(os.path.dirname(os.getcwd()), 'bin/sysconfig.json')
    
    with open(sysconfig_path, 'r') as outfile:
        sysconfig = json.loads(outfile.read())

    clients = list()
    for process_name in sysconfig:
        clients.append(Client(process_name, sysconfig_path))
    
    while True:
        for c in clients:
            for keys, values in c.cvt.items():
                print(c.process_name, round(values,2), keys)
            print('-------------------------')
        sleep(60)
