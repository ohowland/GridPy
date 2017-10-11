from GridPi.Models import EnergyStorage

class VirtualEnergyStorage(EnergyStorage):

    def __init__(self, config_dict):
        EnergyStorage.__init__(self)

        self.init_model(config_dict)

    def __del__(self):
        print('PROCESS INTERFACE:', self.process_name, '-- deconstructed')

    def update(self):

        super(VirtualEnergyStorage, self).update()
