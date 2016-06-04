import json
from pymodbus3.client.sync import ModbusTcpClient
from pymodbus3.payload import BinaryPayloadDecoder
from time import sleep
from threading import Thread


class Client(Thread):
    """ModbusTCPClient polls a Modbus address
    for data returns as dictionary
    """

    def __init__(self, processname, sysconfig_path):
        Thread.__init__(self)
        self.daemon = True
        self.processname = processname

        """PARAMETERS:
        self.reg = [{
            'name': 'modbus register name',
            'ip_add': 'host ip address',
            'mod_add': modbus register address,
            'type': '32bit_float, 16bit_int',
            'value': 'current register value'
            'handle_id': 'internal numeric id for register'
        }]
        """

        self.reg = dict()

        self.loadconfig(processname, sysconfig_path)
        self.client = ModbusTcpClient(self.reg[0]['ip_add'])
        self.initconnection()

        self.start()


    def __del__(self):

        """Teardown"""
        #self.client.close()


    def run(self):

        while True:
            self.read()
            sleep(1)


    def loadconfig(self, processname, filepath):
        
        """Load JSON configuration file """
        with open(filepath, 'r') as outfile:
            self.reg = json.loads(outfile.read())
            
        self.reg = self.reg[processname]['ModbusRegisters']
        i = 0
        for register in self.reg:
            register.update({'value': 0, 'handle_id': i})
            i += 1


    def initconnection(self):
        
        """Initiates the ModbusTCP connection"""
        try:
            self.client.connect()
        except:
            print('Bad IP Address')


    def read(self):

            for reg in self.reg:

                try:

                    """TODO: filter by register_name_list"""

                    if reg['type'] == '32bit_float':
                        read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                        decoded_data = BinaryPayloadDecoder.from_registers(list(reversed(read_data.registers)), endian='>')
                        reg['value'] = decoded_data.decode_32bit_float()

                    elif reg['type'] == '32bit_int':
                        read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                        decoded_data = BinaryPayloadDecoder.from_registers(read_data.registers, endian='>')
                        reg['value'] = decoded_data.decode_32bit_int()

                    elif reg['type'] == '16bit_int':
                        read_data = self.client.read_holding_registers(reg['mod_add'], 1, unit=1)
                        decoded_data = BinaryPayloadDecoder.from_registers(read_data.registers, endian='>')
                        reg['value'] = decoded_data.decode_16bit_int()

                    else:
                        print(reg['type'], 'data type not supported')
                        
                except (AttributeError):
                    print(self.processname, 'write error')
                


    def write(self):

        """TODO: write holding registers"""


    def get(self, name):
        for reg in self.reg:
            if reg['name'] == name:
                return [reg['value']]
        return [None]

