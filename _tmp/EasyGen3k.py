import Models
import Comm


class EasyGen3k(Models.Diesel):

    def __init__(self, config_dict):
        Models.Diesel.__init__(self)

        # Configure model
        self.init_model(config_dict)

        # Configure communication client.
        self.config['comm_client'] = Comm.ModbusClient(self.config['process_name'],
                                                       config_dict['interface_config'])

    def __del__(self):
        self.config['comm_client'].stop()
        print('PROCESS INTERFACE:', self.config['process_name'], '-- deconstructed')

    def update(self):

        super(EasyGen3k, self).update()


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


