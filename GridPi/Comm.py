#!/usr/bin/env python3

"""Modbus.py is an extension of pymodbus3 and the threading module.
    This module contains a modbus Client and Server class.

    TODO:
    1. Understand and implement tighter except clauses. How do we integrate pymodbus3 exceptions into this script?
    2. Proper documentation of parameters and methods.

"""
import time
from pymodbus3.client.sync import ModbusTcpClient
from pymodbus3.payload import BinaryPayloadDecoder
import threading


class ModbusClient(threading.Thread):
    """Define Tag engine to poll MODBUS servers.

    """

    def __init__(self, process_name, interface_config):
        """ interface config
        ('ip_add', '0.0.0.0')
        ('endian', '>')
        ('registers', {
            'type': '32bit_float',
            'name': 'kw',
            'scale': 0.001,
            'mod_add': 50052})
        ('update_rate', 1)

        """
        threading.Thread.__init__(self)

        self.config = interface_config
        self.process_name = process_name

        self.daemon = True  # TODO: this may be threading in 2.7, daemon is method now?

        self.client = None
        self.cvt = dict()
        self.process_stop = False
        self.connected = False
        self.timestamp = str()

        # Initialize Current Value Table (CVT)
        for reg in self.config['registers']:
            self.cvt.update({reg['name']: None})

    def __del__(self):
        """Teardown

        """
        print('MODBUS CLIENT:', self.process_name, '-- deconstructed')

    def run(self):
        """Connect to target and maintain client while loop.

        Call with Thread.start()
        """
        print('MODBUS CLIENT', self.process_name, '-- started')
        self.connect()

        while not self.process_stop:
            if self.connected:
                self._update()
            time.sleep(self.config['update_rate'])

        self.disconnect()
        self.__del__()

    def stop(self):
        """Stop process

        """
        self.process_stop = True

    def connect(self):
        """Connect to target MODBUS server.

        """
        try:
            self.client = ModbusTcpClient(self.config['ip_add'])
            self.client.connect()
            self.connected = True
        except:
            print('MODBUS CLIENT:', self.process_name, '-- unable to connect to target server.')

    def disconnect(self):
        """Disconnect from target MODBUS server.

        """
        try:
            self.client.close()
            self.connected = False
            print('MODBUS CLIENT:', self.process_name, '-- disconnected')
        except:
            print('MODBUS CLIENT:', self.process_name, '-- failed to disconnect from server')

    def _update(self):
        """Poll MODBUS target server.

        Store results in self.cvt
        """
        for reg in self.config['registers']:

            try:

                """TODO: filter by register_name_list"""

                if reg['type'] == '32bit_float':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(
                        list(reversed(read_data.registers)),
                        endian=self.config['endian']
                    )
                    self.cvt[reg['name']] = decoded_data.decode_32bit_float() * reg['scale']

                elif reg['type'] == '32bit_int':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(
                        read_data.registers,
                        endian=self.config['endian']
                    )
                    self.cvt[reg['name']] = decoded_data.decode_32bit_int() * reg['scale']

                elif reg['type'] == '32bit_uint':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 2, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(
                        read_data.registers,
                        endian=self.config['endian']
                    )
                    self.cvt[reg['name']] = decoded_data.decode_32bit_uint() * reg['scale']

                elif reg['type'] == '16bit_int':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 1, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(
                        read_data.registers,
                        endian=self.config['endian']
                    )
                    self.cvt[reg['name']] = decoded_data.decode_16bit_int() * reg['scale']

                elif reg['type'] == '16bit_uint':
                    read_data = self.client.read_holding_registers(reg['mod_add'], 1, unit=1)
                    decoded_data = BinaryPayloadDecoder.from_registers(
                        read_data.registers,
                        endian=self.config['endian']
                    )
                    self.cvt[reg['name']] = decoded_data.decode_16bit_uint() * reg['scale']

                else:
                    print(reg['type'], 'data type not supported')

            except AttributeError:
                print(self.process_name, 'MODBUS CLIENT: Read error')
                # TODO: How to import pymobus3 exceptions?

        self.timestamp = time.ctime()

    def write(self): pass  # TODO: write holding registers
