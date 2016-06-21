import Models
import Comm


class EasyGen3k(Models.Diesel):

    def __init__(self, properties_dict):
        Models.Diesel.__init__(self)

        self.process_name = list(properties_dict.keys())[0]
        self.comm_client = None

        config = properties_dict[self.process_name]

        for key, value in config['model_config'].items():
            if key in self.__dict__.keys():
                self.__dict__[key] = value

        self.comm_client = Comm.ModbusClient(self.process_name, config['interface_config'])

    def __del__(self):
        self.comm_client.stop()
        print('PROCESS INTERFACE:', self.process_name, '-- deconstructed')

if __name__ == '__main__':

    EasyGen = EasyGen3k(
        {
            'Diesel_1': {
                'model_config': {
                    "cap_kw_pos_rated": 20,
                    "cap_kw_neg_rated": 0,
                    "cap_kvar_pos_rated": 12,
                    "cap_kvar_neg_rated": 12,
                    "not_in_dict": 42
                },
                'interface_config': {
                    'ip_add': '0.0.0.0',
                    'endian': '>',
                    'update_rate': 1,
                    'registers': [
                        {
                        'name': 'kw',
                        'mod_add': 50052,
                        'scale': 0.001,
                        'type': '32bit_float'
                        }
                    ]
                    }
                }
        }
    )


