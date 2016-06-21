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