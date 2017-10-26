import logging
from GridPi.ProcessModules import ProcessModule

class SOCPwrCtrl(ProcessModule):

    def __init__(self):
        super(SOCPwrCtrl, self).__init__()
        self.config_module_name = 'SOCPwrCtrl'
        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.config_module_name)

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.config_module_name)

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)  # configure logging
    test_mod = SOCPwrCtrl()