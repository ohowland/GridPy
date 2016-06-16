"""Modbus.py is an extension of pymodbus3 and the threading module.
    This module contains a modbus Client and Server class.

    TODO:
    1. Understand and implement tighter except clauses. How do we integrate pymodbus3 exceptions into this script?
    2. Proper documentation of parameters and methods.

"""
import json
import time
from pymodbus3.client.sync import ModbusTcpClient
from pymodbus3.payload import BinaryPayloadDecoder
import threading


class Client(threading.Thread):
    """Define Tag engine to poll MODBUS servers.

    """

    def __init__(self, process_name, sysconfig_path):
        """ Client expects a process_name by which it can be identified,
        and a path to a json configuration file containing dictionaries
        with key = self.process_name and values = 'register', 'ip_add',
        'endian', 'update_rate'.

        :param sysconfig_path: path to the sysconfig.json configuration file.
        :param process_name: name of this process thread.

        daemon: independent while loop?
        reg: [{
            'name': 'modbus register name',
            'mod_add': modbus register address,
            'type': '32bit_float, 16bit_int',
            'scale' : 'scaling value applied to register'
            }]
        cvt: current value table as dict():
            ('register name_1: current value_1, ...
            'register name_N: current value_N}
        props: MODBUS client properties
            ({'ip_addess': str(), 'endian': str(), update_rate: int()}
        client: pyModbus3 Modbus TCP client object

        """
        threading.Thread.__init__(self)

        # Initiate properties
        self.daemon = True #TODO: this may be threading in 2.7, daemon is method now?
        self.process_name = process_name
        self.sysconfig_path = sysconfig_path
        self.process_stop = False
        self.connected = False

        self.reg = tuple()
        self.prop = dict()
        self.cvt = dict()
        self.timestamp = str()

        # Configure MODBUS client
        with open(self.sysconfig_path, 'r') as outfile:
            raw_reg = json.loads(outfile.read())

        self.prop.update({'ip_add': raw_reg[self.process_name]['ip_add'],
                          'endian': raw_reg[self.process_name]['endian'],
                          'update_rate': raw_reg[self.process_name]['update_rate']
                          })

        self.reg = raw_reg[self.process_name]['registers']

        # Build 'Current Value Table' (CVT)
        for register in self.reg:
            self.cvt.update({register['name']: 0})

    def __del__(self):
        """Teardown

        """
        print('MODBUS CLIENT:', self.process_name, '-- deconstructed')

    def run(self):
        """Connect to target and maintain client while loop.

        """
        self.connect()

        while self.process_stop == False:
            if self.connected == True:
                self.update()
            time.sleep(self.prop['update_rate'])

    def connect(self):
        """Connect to target MODBUS server.

        """
        try:
            self.client = ModbusTcpClient(self.prop['ip_add'])
            self.client.connect()
            self.connected = True
        except:
            print('MODBUS CLIENT:', self.process_name, '-- Unable to connect to target server.')

    def disconnect(self):
        """Disconnect from target MODBUS server.

        """
        self.client.close()
        self.connected = False
        print('MODBUS CLIENT:', self.process_name, '-- process stopped')

    def update(self):
        """Poll MODBUS target server.

        Store results in self.cvt
        """
        for reg in self.reg:

            try:

                """TODO: filter by register_name_list"""

                if reg['type'] == '32bit_float':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(list(reversed(read_data.registers)),
                                                                       endian=self.prop['endian'])
                    self.cvt[reg['name']] = decoded_data.decode_32bit_float() * reg['scale']

                elif reg['type'] == '32bit_int':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(read_data.registers, endian=self.prop['endian'])
                    self.cvt[reg['name']] = decoded_data.decode_32bit_int() * reg['scale']

                elif reg['type'] == '16bit_int':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 1, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(read_data.registers, endian=self.prop['endian'])
                    self.cvt[reg['name']] = decoded_data.decode_16bit_int() * reg['scale']

                else:
                    print(reg['type'], 'data type not supported')

            except AttributeError:
                print(self.process_name, 'MODBUS CLIENT: Read error')
                #TODO: How to import pymobus3 exceptions?

        self.timestamp = time.ctime()

    def write(self):
        return
        # TODO: write holding registers

