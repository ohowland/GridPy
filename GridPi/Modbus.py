import json
from pymodbus3.client.sync import ModbusTcpClient
from pymodbus3.payload import BinaryPayloadDecoder
from threading import Thread
from time import sleep


class Client(Thread):
    """ModbusTCPClient polls a Modbus address
    for data returns as dictionary

    PARAMETERS:
        self.sysconfig_path =
        self.process_name =
        self.reg = [{
        'name': 'modbus register name',
        'ip_add': 'host ip address',
        'mod_add': modbus register address,
        'type': '32bit_float, 16bit_int',
        'scale' : 'scaling value applied to register'
        }]
        self.cvt = {'register name_1: current value_1, ...
                    'register name_N: current value_N}
        self.props = ({'ip_add': str(), 'endian': str(), update_rate: int()
        ip_add = ip address of target
        endian = endianess of target's registers
        update rate = rate of target polling

        self.client = pyModbus3 Modbus TCP client object

        """

    def __init__(self, process_name, sysconfig_path):
        Thread.__init__(self)
        self.daemon = True

        self.process_name = process_name
        self.sysconfig_path = sysconfig_path

        self.reg = tuple()
        self.prop = dict()
        self.cvt = dict()

        # CONFIGURE MODBUS CLIENT
        with open(self.sysconfig_path, 'r') as outfile:
            raw_reg = json.loads(outfile.read())

        self.prop.update({'ip_add': raw_reg[self.process_name]['ip_add'],
                          'endian': raw_reg[self.process_name]['endian'],
                          'update_rate': raw_reg[self.process_name]['update_rate']
                           })

        self.reg = raw_reg[self.process_name]['registers']

        #BUILD CURRENT VALUE TABLE
        for register in self.reg:
            self.cvt.update({register['name']: 0})

        # LAUNCH MODBUS CLIENT
        try:
            self.client = ModbusTcpClient(self.prop['ip_add'])
            self.client.connect()
        except:
            print('modbus error')

        # START PROCESS
        print(self.prop)
        print(self.cvt)
        self.start()

    def __del__(self):
        """Teardown"""

    def run(self):

        while True:
            self.update()
            sleep(self.prop['update_rate'])

    def update(self):

        for reg in self.reg:

            try:

                """TODO: filter by register_name_list"""

                if reg['type'] == '32bit_float':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(list(reversed(read_data.registers)),
                                                                       endian=self.prop['endian'])
                    self.cvt['value'] = decoded_data.decode_32bit_float() * reg['scale']

                elif reg['type'] == '32bit_int':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(read_data.registers, endian=self.prop['endian'])
                    self.cvt['value'] = decoded_data.decode_32bit_int() * reg['scale']

                elif reg['type'] == '16bit_int':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 1, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(read_data.registers, endian=self.prop['endian'])
                    self.cvt['value'] = decoded_data.decode_16bit_int() * reg['scale']

                else:
                    print(reg['type'], 'data type not supported')

            except (AttributeError):
                print(self.processname, 'read error')

    def write(self):

        """TODO: write holding registers"""
