import json

with open('diesel.json', 'w') as outfile:
    json.dump({'ModbusRegisters':[
        {'handle_id': 0 , 'name': 'kW',  'ip_add': '192.168.253.154', 'mod_add': '42', 'type': '32bit_float'},
        {'handle_id': 0 , 'name': 'kVAR', 'ip_add': '192.168.253.154', 'mod_add': '44', 'ype': '32bit_float'}
        ]}, outfile)

with open('battinv.json', 'w') as outfile:
    json.dump({'ModbusRegisters':[
        {'handle_id': 0 , 'name': 'kW',  'ip_add': '192.168.253.154', 'mod_add': '42', 'type': '32bit_float'},
        {'handle_id': 0 , 'name': 'kVAR', 'ip_add': '192.168.253.154', 'mod_add': '44', 'ype': '32bit_float'}
        ]}, outfile)

"""if __name__ == '__main__':
    with open('data.txt', 'r') as outfile:
        j = json.loads(outfile.read())

    for reg in j['ModbusRegisters']:
        print(reg['name'],reg['mod_add'])
"""