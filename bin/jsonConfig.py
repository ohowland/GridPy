import json
from time import sleep

with open('SysConfig.json', 'w') as outfile:
    json.dump(
    {'Diesel1': {
        'ip_add': '192.168.253.165',
        'endian': '>',
        'update_rate': 1,
        'registers': [
            {'name': 'kW', 'mod_add': 50052, 'type': '32bit_int', 'scale': 0.001},
            {'name': 'kVAR', 'mod_add': 50058, 'type': '32bit_int', 'scale': 0.001}]
        },
    'BatteryInverter1': {
        'ip_add': '192.168.253.162',
        'endian': '>',
        'update_rate': 1,
        'registers': [
            {'name': 'kW', 'mod_add': 121, 'type': '32bit_float', 'scale': 1.0},
            {'name': 'kVAR', 'mod_add': 123, 'type': '32bit_float', 'scale': 1.0}]
        },
    'GridIntertie1': {
        'ip_add': '192.168.253.154',
        'endian': '>',
        'update_rate': 1,
        'registers': [
            {'name': 'kW', 'mod_add': 42, 'type': '32bit_float', 'scale': 1.0},
            {'name': 'kVAR', 'mod_add': 44, 'type': '32bit_float', 'scale': 1.0}]
        }}, outfile, sort_keys=True, indent=4)

sleep(1)

with open('SysConfig.json', 'r') as outfile:
    j = json.loads(outfile.read())

for reg in j['Diesel1']['registers']:
    print(reg['name'],reg['mod_add'])
