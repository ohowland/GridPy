import Models
import Comm


class SEL547(Models.GridIntertie):

    def __init__(self, properties_dict):
        Models.GridIntertie.__init__(self)

        self.process_name = list(properties_dict.keys())[0]
        self.comm_client = None

        config = properties_dict[self.process_name]

        for key, value in config['model_config'].items():
            if key in self.__dict__.keys():
                self.__dict__[key] = value

        self.comm_client = Comm.ModbusClient(self.process_name, config['interface_config'])

    def __del__(self):
        self.comm_client.stop()
        self.comm_client.disconnect()
        print('PROCESS INTERFACE:', self.process_name, '-- deconstructed')

    def update(self):

        # Data from comm_client:

        # Numerics
        self.freq = self.comm_client.cvt['freq']
        self.volt = self.comm_client.cvt['volt']
        self.kw = self.comm_client.cvt['kw']
        self.kvar = self.comm_client.cvt['kvar']

        # Booleans
        self.online = False
        self.on_system = True
        self.enabled = True
        self.remote_ctrl = False
        self.grid_forming = False

        # Status Numeric Calcs
        self.cap_kw_pos_avail = self.cap_kw_pos_rated * int(self.enabled)
        self.cap_kw_neg_avail = self.cap_kw_neg_rated * int(self.enabled)
        self.cap_kvar_pos_avail = self.cap_kvar_pos_rated * int(self.enabled)
        self.cap_kvar_neg_avail = self.cap_kvar_neg_rated * int(self.enabled)

        # Status Boolean Calcs
        self.alarm = False
        self.warning = False
        self.caution = False