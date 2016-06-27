import Models
import Comm


class EasyGen3k(Models.Diesel):

    def __init__(self, properties_dict):
        Models.Diesel.__init__(self)

        # Set 'Process Name'.
        self.config['process_name'] = list(properties_dict.keys())[0]

        # Pull configuration data for this process from the properties dictionary passes to the object.
        config = properties_dict[self.config['process_name']]

        # Map configuration file key, values to to model config dictionary keys
        for key, value in config['model_config'].items():
            if key in self.__dict__.keys():
                self.__dict__[key] = value

        # Start communication client.
        self.config['comm_client'] = Comm.ModbusClient(self.process_name, config['interface_config'])

    def __del__(self):
        self.comm_client.stop()
        print('PROCESS INTERFACE:', self.process_name, '-- deconstructed')

    def update(self):

        # Map data from comm_client to model:
        # [freq, volt, kw, kvar]
        for map in self.status.keys():
            if map in self.comm_client.cvt.keys():
                self.status[map] = self.comm_client.cvt[map]
                print(map)

        # Capacity Available
        self.status['cap_kw_pos_avail'] = self.config['cap_kw_pos_rated']*int(self.enabled)
        self.status['cap_kw_neg_avail'] = self.config['cap_kw_neg_rated']*int(self.enabled)
        self.status['cap_kvar_pos_avail'] = self.config['cap_kvar_pos_rated']*int(self.enabled)
        self.status['cap_kvar_neg_avail'] = self.config['cap_kvar_neg_rated']*int(self.enabled)


        """ TBD
        self.freq = self.comm_client.cvt.get('freq', 0)
        self.volt= self.comm_client.cvt.get('volt', 0)
        self.kw = self.comm_client.cvt.get('kw', 0)
        self.kvar = self.comm_client.cvt.get('kvar', 0)

        # Booleans
        self.online = False
        self.on_system = True
        self.enabled = True
        self.remote_ctrl = False
        self.grid_forming = False

        # Status Numeric Calcs


        #Status Boolean Calcs
        self.alarm = False
        self.warning = False
        self.caution = False

        """


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


