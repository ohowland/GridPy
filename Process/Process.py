#!/usr/bin/env python3

import logging
from Process import GraphProcess

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

class ProcessFactory(object):
    """Asset factor for the creating of Asset concrete objects

    """
    def __init__(self):
        self.module_name = self.__module__.split('.')[0]

    def factory(self, configparser):
        """ Factory function for Asset Class objects

        :param config_dict: Configuration dictonary
        :return factory_class: Process Class decendent of type listed in config_dict
        """
        class_type = configparser['class_name']
        new_module = __import__(self.module_name + '.' + 'Process', fromlist=[type])
        #new_pclass = getattr(new_module , 'Process')
        new_class = getattr(new_module, class_type)
        return new_class(configparser)

class ProcessContainer(object):
    def __init__(self):
        self._process_list = list()
        self._process_dict = dict()
        self._ready = False

    @property
    def process_list(self):
        return self._process_list

    @property
    def process_dict(self):
        return self._process_dict

    @property
    def ready(self):
        return self._ready

    def add_process(self, new_process):
        """ Add process to container

        """
        self._ready = False
        self._process_dict.update({new_process.name: new_process})
        self._process_list.append(new_process)

    def sort(self):
        """ Get dependency topological sort of current processes

        """
        temp_graph = GraphProcess.GraphProcess(self)  # Note that self IS a ProcessContainer.
        temp_graph.buildAdjList()
        process_names_topo_sort = GraphProcess.DFS(temp_graph).topologicalSort

        self._process_list = []
        for process_name in process_names_topo_sort:
            logging.debug('PROCESS CONTAINER: sort(): New process added to process_list %s', self.process_dict[process_name])
            self._process_list.append(self.process_dict[process_name])
        logging.debug('PROCESS CONTAINER: sort(): final process_list %s', self.process_list)

        self._ready = True

    def run(self, handle):
        """ Run all processes in container

        """
        logging.debug('PROCESS CONTAINER: Running the following processes', self.process_list)
        if self._ready:
            for process in self._process_list:
                process.run(handle)
        else:
            print('Process Module not Ready')


class ProcessInterface(object):
    def __init__(self):
        self._input = dict()
        self._output = dict()
        self._config = dict()
        self._name = 'UNDEFINED'

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

    @property
    def config(self):
        return self._config

    @property
    def name(self):
        return self._name

    def initProcess(self, config_dict):
        for key, val in config_dict.items():
            if key in self.config.keys():
                if isint(val):
                    val = int(val)
                elif isfloat(val):
                    val = float(val)
                self.config[key] = val

    def run(self, handle):
        self.readInput(handle)
        self.do_work()
        self.writeOutput(handle)

    def readInput(self, handle):
        self._input = handle.read_multi(self.input)

    def writeOutput(self, handle):
        #logging.info('PROCESS INTERFACE: %s writing %s', self.name, self.output)
        handle.write_multi(self.output)

    def do_work(self):
        pass


class SingleProcess(ProcessInterface):
    def __init__(self):
        super(SingleProcess, self).__init__()

class SingleProcessProxy(SingleProcess):
    """ SingleProcessProxy class overrides the run command. These classes are the 'Update Status' and 'Write Control'
        Process that act as markers for beginning and end of the Process Graph. Currently, Update Status and Write
        Control take place in the Asset class. Potentially the responsibility to call the Asset's methods will be
        moved to the corresponding process class, but currently it's cleaner to keep them separate.
    """
    def __init__(self):
        super(SingleProcess, self).__init__()

    def run(self, handle):
        pass


class AggregateProcess(ProcessInterface):
    def __init__(self, process_list):
        super(AggregateProcess, self).__init__()

        self._process_list = process_list

        for process in self._process_list:
            self._input.update(process._input)

    def run(self, handle):
        self.do_work()
        self.writeOutput(handle)


class INV_SOC_PWR_CTRL(SingleProcess):
    def __init__(self, config_dict):
        super(INV_SOC_PWR_CTRL, self).__init__()

        self._name = 'inverter soc power controller'
        self._input.update({'inverter_soc': 0})
        self._config.update({'inverter_target_soc': 0})
        self._output.update({'inverter_kw_setpoint': None})

        self.initProcess(config_dict)
        logging.debug('PROCESS INTERFACE: %s constructed', self.name)

    def do_work(self):
        if self._input['inverter_soc'] < self.config['inverter_target_soc']:
            self._output['inverter_kw_setpoint'] = -50
        elif self._input['inverter_soc'] > self.config['inverter_target_soc']:
            self._output['inverter_kw_setpoint'] = 50

    def __del__(self):
        logging.debug('PROCESS INTERFACE: %s deconstructed', self.name)


class INV_DMDLMT_PWR_CTRL(SingleProcess):
    def __init__(self, config_dict):
        super(INV_DMDLMT_PWR_CTRL, self).__init__()

        self._name = 'inverter demand limiting power controller'
        self._input.update({'grid_kw': 0})
        self._config.update({'grid_kw_export_limit': 0,
                            'grid_kw_import_limit': 0})
        self._output.update({'inverter_kw_setpoint': None})

        self.initProcess(config_dict)
        logging.debug('PROCESS INTERFACE: %s constructed', self.name)

    def do_work(self):
        if self._input['grid_kw'] < 0 and abs(self._input['grid_kw']) > self._config['grid_kw_export_limit']:
            self._output['inverter_kw_setpoint'] =  self._config['grid_kw_export_limit'] + self._input['grid_kw']

        elif self._input['grid_kw'] > self._config['grid_kw_import_limit']:
            self._output['inverter_kw_setpoint'] = self._input['grid_kw'] - self._config['grid_kw_import_limit']

        else:
            self._output['inverter_kw_setpoint'] = 0

    def __del__(self):
        logging.debug('PROCESS INTERFACE: %s deconstructed', self.name)


class INV_UPT_STATUS(SingleProcessProxy):
    def __init__(self, config_dict):
        super(INV_UPT_STATUS, self).__init__()

        self._name = 'inverter update status'
        self._input = dict()   # No input, acts as root nodes
        self._config.update({'asset_ref': None})  # TODO: asset_ref in update status process, or use asset directly?
        self._output.update({'inverter_soc': None,
                            'inverter_kw': None})

        self.initProcess(config_dict)
        logging.debug('PROCESS MODULE: %s constructed', self.name)

    def do_work(self):
        ''' Using the input, generate the output.

        '''

    def __del__(self):
        logging.debug('PROCESS MODULE: %s deconstructed', self.name)


class INV_WRT_CTRL(SingleProcessProxy):
    def __init__(self, config_dict):
        super(INV_WRT_CTRL, self).__init__()

        self._name = 'inverter write control'
        self._input.update({'inverter_kw_setpoint': 0})
        self._config.update({'asset_ref': None})
        self._output = dict()

        self.initProcess(config_dict)
        logging.debug('PROCESS INTERFACE: %s constructed', self.name)

    def do_work(self):
        """ Call Write Tagbus to Asset

        """
        pass

    def __del__(self):
        logging.debug('PROCESS INTERFACE: %s deconstructed', self.name)


class GRID_UPT_STATUS(SingleProcessProxy):
    def __init__(self, config_dict):
        super(GRID_UPT_STATUS, self).__init__()

        self._name = 'grid update status'
        self._input = dict()  # Empty input, acts as root node
        self._config.update({'asset_ref': None})
        self._output.update({'grid_kw': None})

        self.initProcess(config_dict)
        logging.debug('PROCESS INTERFACE: %s constructed', self.name)

    def do_work(self):
        pass
        # self._output['grid_kw'] = 100

    def __del__(self):
        logging.debug('PROCESS INTERFACE: %s deconstructed', self.name)


class AggregateProcessSummation(AggregateProcess):
    def __init__(self, process_list):
        super(AggregateProcessSummation, self).__init__(process_list)

        self._name = 'aggregate process summation'

        logging.debug('PROCESS INTERFACE: %s constructed', self.name)

    def do_work(self):
        summation = dict()
        for process in self._process_list:
            process.do_work()
            for key, val in process._output.items():
                try:
                    summation[key] += val
                except:
                    summation[key] = val
        self._output = summation

    def __del__(self):
        logging.debug('PROCESS INTERFACE: %s deconstructed', self.name)