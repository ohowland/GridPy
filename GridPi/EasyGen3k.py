import json
import os
import Models

class EasyGen3k(Models.Diesel):

    def __init__(self, properties_dict):
        Models.Diesel.__init__(self)

        self.process_name = properties_dict.keys[1]
        self.model_config = properties_dict['ModelConfiguration']
        self.interface_config = properties_dict['InterfaceConfiguration']

        # Build 'Current Value Table' (CVT)
        for register in self.interface_config['registers']:
            self.cvt.update({register['name']: 0})

        #TODO: Map register fetch with

        def update(self): pass

if __name__ == '__main__':

    EasyGen = EasyGen3k(
        {
            'Diesel_1': {
                'ModelConfiguration': {
                    'kw_rated': 20
                },
                'InterfaceConfiguration': {
                    'ip_add': '0.0.0.0',
                    'endian': '>',
                    'update_rate': 1,
                    'registers': {
                        'name': 'kw',
                        'mod_add': 50052,
                        'scale': 0.001,
                        'type': '32bit_float'
                    }
                    }
                }
        }
    )


