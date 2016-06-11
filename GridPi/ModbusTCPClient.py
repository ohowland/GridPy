from pymodbus3.client.sync import ModbusTcpClient
from pymodbus3.payload import BinaryPayloadDecoder
from time import sleep


class ModbusTCPClient(object):
    """ModbusTCPClient polls a Modbus address
    for data returns as dictionary
    """

    def __init__(self, filepath):

        """PARAMETERS:
        self.config_path = Location of the configuration file
            for this deployment.
        self.reg = [{
            'name' : 'modbus register name',
            'ip' : 'host ip address',
            'address' : modbus register address,
            'type' : '32bit_float, 16bit_int',
            'value' : 'current register value'
        }]
        """

        self.config_path = filepath
        self.reg = dict()

        self.load_config(self.config_path)
        self.client = ModbusTcpClient(self.reg[0]['ip'])

    def __del__(self):

        """Teardown"""

        self.client.close()

    def load_config(self, filepath):

        """Take .xml or .json file
        and convert to list of dictonaries in the form
        of self.registers
        """

    def init_connection(self):

        """Initiates the ModbusTCP connection"""

        try:
            self.client.connect()
        except:
            print('Bad IP Address')

    def read(self):

        for register in self.reg:

            '''TODO: filter by register_name_list'''

            if register['type'] == '32bit_float':
                read_data = self.client.read_holding_registers(register['address'], 2, unit=1)
                decoded_data = BinaryPayloadDecoder.from_registers(list(reversed(read_data.registers)), endian='>')
                register['value'] = decoded_data.decode_32bit_float()

            elif register['type'] == '16bit_int':
                read_data = self.client.read_holding_registers(register['address'], 1, unit=1)
                decoded_data = BinaryPayloadDecoder.from_registers(read_data.registers, endian='>')
                register['value'] = decoded_data.decode_16bit_int()

            else:
                print(register['type'], 'data type not supported')

    def write(self):

        """TODO: write holding registers"""

    def get(self, name):
        for reg in self.reg:
            if reg['name'] == name:
                return [reg['value']]
            else:
                return [0]


if __name__ == '__main__':

    ModTCP = ModbusTCPClient('C:/')
    ModTCP.init_connection()

    while True:
        ModTCP.read()

        print(ModTCP.get('kW'))
        sleep(1)
        print(ModTCP.get('kVAR'))
        sleep(1)
