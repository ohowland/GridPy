import Comm

from GridPi.lib import models


class SEL547(models.GridIntertie):

    def __init__(self, config_dict):
        models.GridIntertie.__init__(self)

        self.init_model(config_dict)

        # Start communication client.
        self.config['comm_client'] = Comm.ModbusClient(self.config['process_name'],
                                                       config_dict['interface_config'])

    def __del__(self):
        self.config['comm_client'].stop()
        print('PROCESS INTERFACE:', self.config['process_name'], '-- deconstructed')

    def update(self):

        super(SEL547, self).update()
