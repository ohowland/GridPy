from Models import GridIntertie

class VirtualGridIntertie(GridIntertie):

    def __init__(self, config_dict):
        GridIntertie.__init__(self)

        self.init_model(config_dict)

    def __del__(self):
        print('PROCESS INTERFACE:', self.process_name, '-- deconstructed')

    def update(self):

        super(VirtualGridIntertie, self).update()
