"""Create a systemconfig.json file


"""

import json
import os

# Build MODBUS client configuration from local configuration files
sysconfig_name = 'sysconfig.ini'
key = 'config_dict'
sysconfig = dict()

files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.json')]

i = 0
for f in files:
    try:
        with open(f, 'r') as outfile:
            component_config = json.loads(outfile.read())

        if key in component_config.keys():
            sysconfig.update({'device_'+str(i): component_config[key]})
            print(f, 'added to system configuration')
        i =++ 1
    except:
        print(f, 'not config file')
        
with open(sysconfig_name, 'w') as outfile:
    json.dump(sysconfig, outfile, sort_keys=True, indent=4)
