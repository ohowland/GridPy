"""Create a systemconfig.json file


"""

import json
import os

# Build MODBUS client configuration from local configuration files
sysconfig_name = 'sysconfig.ini'
key = 'model_config'
sysconfig = dict()

files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.json')]

for f in files:
    try:
        with open(f, 'r') as outfile:
            component_config = json.loads(outfile.read())

        if key in component_config[list(component_config)[0]]:
            sysconfig.update(component_config)
            print(f, 'added to system configuration')
    except:
        print(f, 'not config file')
        
with open(sysconfig_name, 'w') as outfile:
    json.dump(sysconfig, outfile, sort_keys=True, indent=4)
