"""GridPi acts as the software entry point.

1. Initialize Models
    a. Configure with data from sysconfig.json.
    b. Initialize communication abstraction
        I. Load abstraction for Model
.       II. Initialize modbus clients
            A. Instantiate object and launch thread.
            B. Tie Modbus client to a process.
2. Initialize Dispatch
    a. Configure with data from sysconfig.json
    b. Instantiate object
    c. Run

Modbus
Dispatch
Models
"""

import os
import json
import EasyGen3k # eventually put this in an interface.py or __init__.py?

def config_process(model, process, process_list):
    process.process_name = model.keys[1]
    process.model_config = model['model_config']
    process.interface_config = model['interface_config']
    return(process_list.append(process))

if __name__ == '__main__':

    # Initialize
    sysconfig_path = os.path.join(os.path.dirname(os.getcwd()), 'bin/sysconfig.json')

    with open(sysconfig_path, 'r') as outfile:
        sysconfig = json.loads(outfile.read())

    proc_list = list()
    for model in sysconfig:

        if model['model_class'] == 'diesel':
            if model['interface_class'] == 'easygen3k':
                proc = EasGen3k()
                proc_list = config_process(model, proc, proc_list)

            else:
                raise ValueError('diesel model interface class is undefined')
        #elif process['ModelClass'] == 'batteryinverter':
        #    if process['InterfaceClass'] == 'GFIPM3k':
        #        process_list.append(GFIPM3k(process))
        #    else:
        #        print(process, 'interface class is undefined.')

        else:
            raise ValueError('model class is undefined')



'''
    # Create MODBUS Client objects
    clients = list()
    for process_name in sysconfig:
        clients.append(Modbus.Client(process_name, sysconfig_path))
        print('PROCESS CREATED:', process_name)

    time.sleep(1)

    # Start MODBUS Clients
    for client in clients:
        client.start()
        print('PROCESS STARTED:', client.process_name, '-- IP:', client.prop['ip_add'])

    time.sleep(1)

#    while True:
    for client in clients:
        print('-------------------------')
        for keys, values in client.cvt.items():
            print(client.process_name, round(values,2), keys)
    time.sleep(5)

    for client in clients:
        client.process_stop = True
        client.join()
'''

print('Ending GridPi')
