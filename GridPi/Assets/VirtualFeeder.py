from Models import Feeder

class VirtualFeeder(Feeder):

    def __init__(self, config_dict):
        Feeder.__init__(self)

        self.init_model(config_dict)

    def __del__(self):
        print('PROCESS INTERFACE:', self.process_name, '-- deconstructed')

    def update(self):

        super(VirtualFeeder, self).update()
