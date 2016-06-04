import json
from time import sleep

with open('SysConfig.json', 'w') as outfile:
    json.dump(
    {'Diesel1': {
        'ModbusRegisters': [
            {'name': 'kW',  'ip_add': '192.168.253.165', 'mod_add': 50052, 'type': '32bit_int', 'scale': 1},
            {'name': 'kVAR', 'ip_add': '192.168.253.165', 'mod_add': 50058, 'type': '32bit_int', 'scale': 1}]
        },
    'BatteryInverter1': {
        'ModbusRegisters': [
            {'name': 'kW',  'ip_add': '192.168.253.162', 'mod_add': 121, 'type': '32bit_float', 'scale': 1},
            {'name': 'kVAR', 'ip_add': '192.168.253.162', 'mod_add': 123, 'type': '32bit_float', 'scale': 1}]
        },
    'GridIntertie1': {
        'ModbusRegisters': [
            {'name': 'kW',  'ip_add': '192.168.253.154', 'mod_add': 42, 'type': '32bit_float', 'scale': 1},
            {'name': 'kVAR', 'ip_add': '192.168.253.154', 'mod_add': 44, 'type': '32bit_float', 'scale': 1}]
        }}, outfile, sort_keys=True, indent=4)
sleep(1)

with open('SysConfig.json', 'r') as outfile:
    j = json.loads(outfile.read())

for reg in j['Diesel1']['ModbusRegisters']:
    print(reg['name'],reg['mod_add'])
