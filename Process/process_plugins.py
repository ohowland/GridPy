from Process import process_core
import logging


class SystemRemoteControl(process_core.SingleProcess):
    def __init__(self, config_dict):
        super(SystemRemoteControl, self).__init__()
        try:
            self.ess = config_dict['target_inverter']
            self.feeder = config_dict['target_feeder']
            self.grid = config_dict['target_grid_intertie']
        except KeyError:
            self.ess = 'inverter'
            self.feeder = 'feeder'
            self.grid = 'grid'
            logging.warning('%s: using default component names', self.__class__.__name__)

        self.ess_run =        (self.ess, 'control', 'run')
        self.ess_run_req =    (self.ess, 'control', 'run_request')
        self.ess_enable =     (self.ess, 'control', 'enable')
        self.ess_enabled =    (self.ess, 'status', 'enabled')
        self.feeder_run =     (self.feeder, 'control', 'run')
        self.feeder_run_req = (self.feeder, 'control', 'run_request')
        self.feeder_enable =  (self.feeder, 'control', 'enable')
        self.feeder_enabled = (self.feeder, 'status', 'enabled')
        self.grid_run =       (self.grid, 'control', 'run_breaker')
        self.grid_run_req =   (self.grid, 'control', 'run_request')
        self.grid_enable =    (self.grid, 'control', 'enable')
        self.grid_enabled =   (self.grid, 'status', 'enabled')

        self._name = 'system remote control'
        self._input.update({self.grid_enabled: 0,
                            self.feeder_enabled: 0,
                            self.ess_enabled: 0,
                            self.grid_run_req: 0,
                            self.feeder_run_req: 0,
                            self.ess_run_req: 0})

        self._output.update({self.ess_run: 0,
                             self.grid_run: 0,
                             self.feeder_run: 0})

        self.configure_process(config_dict)
        logging.debug('PROCESS INTERFACE: %s constructed', self.name)

    def do_work(self):
        self._output[self.ess_run] = self._input[self.ess_enabled] and \
                                          self._input[self.ess_run_req]

        self._output[self.feeder_run] = self._input[self.feeder_enabled] and \
                                                  self._input[self.feeder_run_req]

        self._output[self.grid_run] = self._input[self.grid_enabled] and \
                                                self._input[self.grid_run_req]


class EssSocPowerController(process_core.SingleProcess):
    def __init__(self, config_dict):
        super(EssSocPowerController, self).__init__()

        try:
            self.ess = config_dict['target_inverter']
        except KeyError:
            self.ess = 'inverter'
            logging.warning('%s: target_inverter not set, defaulting to "%s"',
                            self.__class__.__name__, self.ess)

        self._name = self.ess + ' soc power controller'

        # Define tuples for parameter access
        self.soc = (self.ess, 'status', 'soc')
        self.target_soc = (self.ess, 'config', 'target_soc')
        self.ess_kw_sp = (self.ess, 'control', 'kw_setpoint')

        # Define input/output dependencies
        self._input.update({self.soc: None,
                            self.target_soc: None})

        self._output.update({self.ess_kw_sp: None})

        self.configure_process(config_dict)
        logging.debug('%s: %s constructed', self.__class__.__name__, self.name)

    def do_work(self):
            if self.input[self.soc] < self.input[self.target_soc]:
                self._output[ self.ess_kw_sp] = -50
            elif self.input[self.soc] > self.input[self.target_soc]:
                self._output[ self.ess_kw_sp] = 50

    def __del__(self):
        pass
        #logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)


class EssDemandLimitPowerController(process_core.SingleProcess):
    def __init__(self, config_dict):
        super(EssDemandLimitPowerController, self).__init__()

        try:
            self.ess = config_dict['target_inverter']
        except KeyError:
            self.ess = 'inverter'
            logging.warning('%s: target_inverter not set, defaulting to "%s"',
                            self.__class__.__name__, self.ess)
        try:
            self.grid = config_dict['target_grid_intertie']
        except KeyError:
            self.grid = 'grid'
            logging.warning('%s: target_grid_interconnect not set, defaulting to "%s"',
                            self.__class__.__name__, self.grid)

        self._name = self.ess + ' demand limiting power controller'

        # Define tuples for parameter access
        self.grid_kw = (self.grid, 'status', 'kw')
        self.grid_kw_export_limit = (self.grid, 'config', 'kw_export_limit')
        self.grid_kw_import_limit = (self.grid, 'config', 'kw_import_limit')
        self.ess_kw_sp = (self.ess, 'control', 'kw_setpoint')



        self._input.update({self.grid_kw: None,
                            self.grid_kw_export_limit: None,
                            self.grid_kw_import_limit: None})

        self._output.update({self.ess_kw_sp: None})

        self.configure_process(config_dict)
        logging.debug('%s: %s constructed', self.__class__.__name__, self.name)

    def do_work(self):

        if self._input[self.grid_kw] < 0 and abs(self._input[self.grid_kw]) > self._input[self.grid_kw_export_limit]:
            self._output[self.ess_kw_sp] =  self._input[self.grid_kw_export_limit] + self._input[self.grid_kw]

        elif self._input[self.grid_kw] > self._input[self.grid_kw_import_limit]:
            self._output[self.ess_kw_sp] = self._input[self.grid_kw] - self._input[self.grid_kw_import_limit]
        else:
            self._output[self.ess_kw_sp] = 0

    def __del__(self):
        pass
        #logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)


class EssUpdateStatus(process_core.SingleProcessProxy):
    def __init__(self, config_dict):
        super(EssUpdateStatus, self).__init__()
        try:
            self.ess = config_dict['target_inverter']
        except KeyError:
            self.ess = 'inverter'
            logging.warning('%s: target_inverter not set, defaulting to "%s"',
                            self.__class__.__name__, self.ess)

        self._name = self.ess + ' update status'

        self.soc = (self.ess, 'status', 'soc')
        self.kw = (self.ess, 'status', 'kw')

        self._input = dict()   # No input, acts as root nodes
        self._output.update({self.soc: None,
                             self.kw: None})

        self.configure_process(config_dict)
        logging.debug('%s: %s constructed', self.__class__.__name__, self.name)
    def do_work(self):
        ''' Using the input, generate the output.

        '''

    def __del__(self):
        pass
        #logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)


class EssWriteControl(process_core.SingleProcessProxy):
    def __init__(self, config_dict):
        super(EssWriteControl, self).__init__()

        try:
            self.ess = config_dict['target_inverter']
        except KeyError:
            self.ess = 'inverter'
            logging.warning('%s: target_inverter not set, defaulting to "%s"',
                            self.__class__.__name__, self.ess)

        self._name = self.ess + ' write control'

        self.ess_kw_sp = (self.ess, 'control', 'kw_setpoint')

        self._input.update({self.ess_kw_sp: 0})
        self._output = dict()

        self.configure_process(config_dict)
        logging.debug('%s: %s constructed', self.__class__.__name__, self.name)

    def do_work(self):
        """ Call Write Tagbus to Asset

        """
        pass

    def __del__(self):
        pass
        #logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)


class GridUpdateStatus(process_core.SingleProcessProxy):
    def __init__(self, config_dict):
        super(GridUpdateStatus, self).__init__()

        try:
            self.grid = config_dict['target_grid_intertie']
        except KeyError:
            self.grid = 'grid'
            logging.warning('%s: target_grid_interconnect not set, defaulting to "%s"',
                            self.__class__.__name__, self.grid)

        self._name = self.grid + ' update status'

        self.grid_kw = (self.grid, 'status', 'kw')

        self._input = dict()  # Empty input, acts as root node
        self._output.update({self.grid: None})

        self.configure_process(config_dict)
        logging.debug('%s: %s constructed', self.__class__.__name__, self.name)

    def do_work(self):
        pass

    def __del__(self):
        pass
        #logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)


class AggregateProcessSummation(process_core.AggregateProcess):
    def __init__(self, process_list):
        super(AggregateProcessSummation, self).__init__(process_list)

        self._name = 'aggregate process summation'

        logging.debug('%s: %s constructed', self.__class__.__name__, self.name)

    def do_work(self):
        summation = dict()
        for process in self._process_list:
            for key, val in process._output.items():
                try:
                    summation[key] += val
                except:
                    summation[key] = val
        self._output = summation

    def __del__(self):
        pass
        #logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)