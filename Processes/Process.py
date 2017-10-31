#!/usr/bin/env python3

import logging

class ProcessFactory(object):
    """Asset factor for the creating of Asset concrete objects

    """
    def __init__(self, module_name):

        self.module_name = module_name

    def factory(self, config_dict):
        """ Factory function for Asset Class objects

        :param config_dict: Configuration dictonary
        :return factory_class: Process Class decendent of type listed in config_dict
        """
        class_type = config_dict['model_config']['class_name']
        new_module = __import__(self.module_name + '.' + class_type, fromlist=[type])
        new_class = getattr(new_module, class_type)
        return new_class(config_dict)

class ProcessInterface(object):
    def __init__(self):
        self.input = dict()
        self.output = dict()
        self.config = dict()
        self.config_module_name = 'empty'

    def run_process(self, handle):
        self.read_input(handle)
        self.do_work()
        self.write_output(handle)
        return

    def read_input(self, handle):
        self.input = handle.read(self.input)
        return

    def write_output(self, handle):
        for key, val in self.output.items():
            handle.write(key, val)
        return

    def do_work(self):
        return

class SingleProcess(ProcessInterface):
    def __init__(self):
        super(SingleProcess, self).__init__()

class AggregateProcess(ProcessInterface):
    def __init__(self):
        super(AggregateProcess, self).__init__()

        self.process_list = list()

    def run_process(self, handle):
        self.do_work()
        self.write_output(handle)

class INV_SOC_PWR_CTRL(SingleProcess):
    def __init__(self):
        super(INV_SOC_PWR_CTRL, self).__init__()

        self.config_module_name = 'inverter soc power controller'
        self.input['inverter_soc'] = None
        self.output['inverter_kw_setpoint'] = None

        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.config_module_name)

    def do_work(self):
        self.output['inverter_kw_setpoint'] = 50

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.config_module_name)

class INV_DMDLMT_PWR_CTRL(SingleProcess):
    def __init__(self):
        super(INV_DMDLMT_PWR_CTRL, self).__init__()

        self.config_module_name = 'inverter demand limiting power controller'
        self.input['grid_kw'] = None
        self.output['inverter_kw_setpoint'] = None

        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.config_module_name)

    def do_work(self):
        self.output['inverter_kw_setpoint'] = 25

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.config_module_name)

class AggregateProcessSummation(AggregateProcess):
    def __init__(self):
        super(AggregateProcessSummation, self).__init__()

        self.config_module_name = 'aggregate process summation'

        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.config_module_name)

    def do_work(self):
        summation = dict()
        for process in self.process_list:
            process.do_work()
            for key, val in process.output.items():
                try:
                    summation[key] += val
                except:
                    summation[key] = val
        self.output = summation

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.config_module_name)