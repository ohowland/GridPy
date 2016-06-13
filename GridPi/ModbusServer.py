from pymodbus3.client.sync import ModbusTcpClient
from pymodbus3.payload import BinaryPayloadDecoder
import json


class Client(object):
    """ModbusTCPClient polls a Modbus address
    for data returns as dictionary
    """

    def __init__(self, filepath):

        """PARAMETERS:
        self.config_path = Location of the configuration file
            for this deployment.
        self.reg = [{
            'name': 'modbus register name',
            'ip_add': 'host ip address',
            'mod_add': modbus register address,
            'type': '32bit_float, 16bit_int',
            'value': 'current register value'
        }]
        """

        self.config_path = filepath
        self.reg = dict()

        self.load_config(self.config_path)

        self.reg = self.reg['ModbusRegisters']
        self.client = ModbusTcpClient(self.reg[0]['ip_add'])

    def __del__(self):

        """Teardown"""
        #self.client.close()

    def load_config(self, filepath):
        """Load JSON configuration file """
        with open(filepath, 'r') as outfile:
            self.reg = json.loads(outfile.read())

    def init_connection(self):
        """Initiates the ModbusTCP connection"""
        try:
            self.client.connect()
        except:
            print('Bad IP Address')

    def read(self):

        for reg in self.reg:

            """TODO: filter by register_name_list"""

            if reg['type'] == '32bit_float':
                read_data = self.client.read_holding_registers(reg['address'], 2, unit=1)
                decoded_data = BinaryPayloadDecoder.from_registers(list(reversed(read_data.registers)), endian='>')
                reg['value'] = decoded_data.decode_32bit_float()

            elif reg['type'] == '16bit_int':
                read_data = self.client.read_holding_registers(reg['address'], 1, unit=1)
                decoded_data = BinaryPayloadDecoder.from_registers(read_data.registers, endian='>')
                reg['value'] = decoded_data.decode_16bit_int()

            else:
                print(reg['type'], 'data type not supported')

    def write(self):

        """TODO: write holding registers"""

    def get(self, name):
        for reg in self.reg:
            if reg['name'] == name:
                return [reg['value']]
            else:
                return [None]