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

"""

import os
import json
import time
import EasyGen3k, SEL547 # eventually put this in an interface.py or __init__.py?

if __name__ == '__main__':

    # Read system configuration
    sysconfig_path = os.path.join(os.path.dirname(os.getcwd()), 'bin/sysconfig.ini')

    with open(sysconfig_path, 'r') as outfile:
        sysconfig = json.loads(outfile.read())

    # Configure processes
    proc_list = list()
    for proc_config in sysconfig:
        proc_config_dict = sysconfig.get(proc_config, {})

        if proc_config_dict['interface_class'] == 'easygen3k':
            proc_list.append(EasyGen3k.EasyGen3k({proc_config: proc_config_dict}))
            print('Found EasyGen3k')

        elif proc_config_dict['interface_class'] == 'sel547':
            proc_list.append(SEL547.SEL547({proc_config: proc_config_dict}))
            print('Found SEL547')

        else:
            raise ValueError('interface class is undefined')

    # Start processes communication
    for proc in proc_list:
        proc.comm_client.start()


    for proc in proc_list:
        for x in range(0, 3):
            time.sleep(2)
            proc.update()
            print(proc.process_name,': \n',
                proc.kw, 'kW \n',
                proc.kvar, 'kVAR \n',
                proc.freq, 'Hz \n',
                proc.volt, 'V \n')

        proc.comm_client.stop()

print('Ending GridPi')
