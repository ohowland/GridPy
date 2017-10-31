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
        class_type = config_dict['model_config']['class_name'] # TODO: This sucks re-write tomorrow morning.
        new_module = __import__(self.module_name)
        new_pclass = getattr(new_module , 'Process')
        new_class = getattr(new_pclass, class_type)
        return new_class(config_dict)

    def get_class(kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

class ProcessInterface(object):
    def __init__(self):
        self.input = dict()
        self.output = dict()
        self.config = dict()

        self.name = 'empty'

    def init_process(self, config_dict):
        for key, val in config_dict['model_config'].items():
            if key in self.config.keys():
                self.config[key] = val

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
    def __init__(self, config_dict):
        super(INV_SOC_PWR_CTRL, self).__init__()
        self.init_process(config_dict)

        self.name = 'inverter soc power controller'
        self.input.update({'inverter_soc': 0})
        self.config.update({'inverter_target_soc': 0})
        self.output.update({'inverter_kw_setpoint': None})

        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.name)

    def do_work(self):
        if self.input['inverter_soc'] < self.config['inverter_target_soc']:
            self.output['inverter_kw_setpoint'] = -50
        elif self.input['inverter_soc'] > self.config['inverter_target_soc']:
            self.output['inverter_kw_setpoint'] = 50

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.name)


class INV_DMDLMT_PWR_CTRL(SingleProcess):
    def __init__(self, config_dict):
        super(INV_DMDLMT_PWR_CTRL, self).__init__()
        self.init_process(config_dict)

        self.name = 'inverter demand limiting power controller'
        self.input.update({'grid_kw': 0})
        self.config.update({'grid_kw_export_limit': 0,
                            'grid_kw_import_limit': 0})
        self.output.update({'inverter_kw_setpoint': None})

        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.name)

    def do_work(self):

        if self.input['grid_kw'] < 0 and abs(self.input['grid_kw']) > self.config['grid_kw_export_limit']:
            self.output['inverter_kw_setpoint'] =  self.config['grid_kw_export_limit'] + self.input['grid_kw']

        elif self.input['grid_kw'] > self.config['grid_kw_import_limit']:
            self.output['inverter_kw_setpoint'] = self.input['grid_kw'] - self.config['grid_kw_import_limit']

        else:
            self.output['inverter_kw_setpoint'] = 0

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.name)


class INV_UPT_STATUS(SingleProcess):
    def __init__(self, config_dict):
        super(INV_UPT_STATUS, self).__init__()
        self.init_process(config_dict)

        self.name = 'inverter update status'
        self.input = dict()   # No input, acts as root nodes
        self.config.update({'asset_ref': None})  # TODO: asset_ref in update status process, or use asset directly?
        self.output.update({'inverter_soc': None,
                            'inverter_kw': None})

        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.name)

    def do_work(self):
        ''' Call on asset to update tagbus from self

        '''
        self.output['inverter_soc'] = 0.5
        self.output['inverter_kw'] = 0.0

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.name)


class INV_WRT_CTRL(SingleProcess):
    def __init__(self, config_dict):
        super(INV_WRT_CTRL, self).__init__()
        self.init_process(config_dict)

        self.name = 'inverter write control'
        self.input.update({'inverter_kw_setpoint': 0})
        self.config.update({'asset_ref': None})
        self.output = dict()

        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.name)

    def do_work(self):
        """ Call Write Tagbus to Asset

        """
        pass

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.name)


class GRID_UPT_STATUS(SingleProcess):
    def __init__(self, config_dict):
        super(GRID_UPT_STATUS, self).__init__()
        self.init_process(config_dict)

        self.name = 'grid update status'
        self.input = dict()  # Empty input, acts as root node
        self.config.update({'asset_ref': None})
        self.output.update({'grid_kw': None})

        logging.debug('PROCESS MODULE INTERFACE: %s constructed', self.name)

    def do_work(self):
        self.output['grid_kw'] = 100

    def __del__(self):
        logging.debug('PROCESS MODULE INTERFACE: %s deconstructed', self.name)


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