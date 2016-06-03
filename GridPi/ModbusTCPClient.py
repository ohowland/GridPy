from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from time import sleep

class ModbusTCPClient(object):

    '''ModbusTCPClient polls a MODBUS address
    for data returns as dictonary
    '''

    def __init__(self, FilePath):

        '''PARAMETERS:
        self.config_path = Location of the configuration file
            for this deployment.
        self.reg = [{
            'name' : 'modbus register name',
            'ip' : 'host ip address',
            'address' : modbus register address,
            'type' : '32bit_float, 16bit_int',
            'value' : 'current register value'
        }]
        '''

        self.config_path = FilePath
        self.reg = [{
            'name' : 'kW',
            'ip' : '192.168.253.154',
            'address' : 42,
            'type' : '32bit_float',
            'value' : 0
        }, {
            'name' : 'kVAR',
            'ip' : '192.168.253.154',
            'address' : 44,
            'type' : '32bit_float',
            'value' : 0
        }]

        self.LoadConfig(self.config_path)


    def __del__(self):

        '''Teardown'''

        self.client.close()


    def LoadConfig(self, FilePath):

        '''Take .xml or .json file
        and convert to list of dictonaries in the form
        of self.registers
        '''


    def InitConnection(self):

        '''Initiates the ModbusTCP connection'''

        try:
            self.client = ModbusTcpClient(self.reg[0]['ip'])
            self.client.connect()
        except:
            print('Bad IP Address')


    def read(self, register_name_list=[]):

        for register in self.reg:

            '''TODO: filter by register_name_list'''

            if register['type'] == '32bit_float':
                read_data = self.client.read_holding_registers(register['address'], 2, unit=1)
                decoded_data = BinaryPayloadDecoder.fromRegisters(list(reversed(read_data.registers)), endian='>')
                register['value'] = decoded_data.decode_32bit_float()

            elif register['type'] == '16bit_int':
                read_data = self.client.read_holding_registers(register['address'], 1, unit=1)
                decoded_data = BinaryPayloadDecoder.fromRegisters((read_data.registers), endian='>')
                register['value'] = decoded_data.decode_16bit_int()

            else:
                Print(register['type'], 'data type not supported')

    def write(self):

        '''TODO: write holding registers'''

    def get(self, name):
        for reg in self.reg:
            if reg['name'] == name:
                return[reg['value']]
            else:
                return[0]


if __name__ == '__main__':

    ModTCP = ModbusTCPClient('C:/')
    ModTCP.InitConnection()

    while True:
        ModTCP.read()
        
        print(ModTCP.get('kW'))
        sleep(1)
        print(ModTCP.get('kVAR'))
        sleep(1)


