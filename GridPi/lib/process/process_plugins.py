import logging

from GridPi.lib.process import process_core


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

        self.ess_run = (self.ess, 'control', 'run')
        self.ess_run_req = (self.ess, 'control', 'run_request')
        self.ess_enable = (self.ess, 'control', 'enable')
        self.ess_enabled = (self.ess, 'status', 'enabled')
        self.feeder_run = (self.feeder, 'control', 'run')
        self.feeder_run_req = (self.feeder, 'control', 'run_request')
        self.feeder_enable = (self.feeder, 'control', 'enable')
        self.feeder_enabled = (self.feeder, 'status', 'enabled')
        self.grid_run = (self.grid, 'control', 'run_breaker')
        self.grid_run_req = (self.grid, 'control', 'run_request')
        self.grid_enable = (self.grid, 'control', 'enable')
        self.grid_enabled = (self.grid, 'status', 'enabled')

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

        # Name assets
        self._ess = 'ess'
        self._name = 'Inverter SOC power controller'

        # Define input/output dependencies
        self._input.update({self.tag(self._ess, 0, 'status', 'soc'): None,
                            self.tag(self._ess, 0, 'config', 'target_soc'): None})

        self._output.update({self.tag(self._ess, 0, 'control', 'kw_setpoint'): None})

        self.configure_process(config_dict)
        logging.debug('%s: %s constructed', self.__class__.__name__, self._name)

    def do_work(self):

        # Use asset dummy dictonaries to clarify the process code.
        inverter = {}
        inverter.update({key.param_name: val for key, val in self._input.items()})
        inverter.update({key.param_name: val for key, val in self._output.items()})

        if inverter['soc'] < inverter['target_soc']:
            inverter['kw_setpoint'] = -50
        elif inverter['soc'] > inverter['target_soc']:
            inverter['kw_setpoint'] = 50

        # push values back into output
        self._output.update({tag: inverter[tag.param_name] for tag in self._output.keys()})

    def __del__(self):
        pass
        # logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)


class EssDemandLimitPowerController(process_core.SingleProcess):
    def __init__(self, config_dict):
        super(EssDemandLimitPowerController, self).__init__()

        self._ess = 'ess'
        self._grid = 'grid'
        self._name = 'ESS demand limiting power controller'

        self._input.update({self.tag(self._grid, 0, 'status', 'kw'): None,
                            self.tag(self._grid, 0, 'config', 'kw_export_limit'): None,
                            self.tag(self._grid, 0, 'config', 'kw_import_limit'): None})


        self._output.update({self.tag(self._ess, 0, 'control', 'kw_setpoint'): None})

        self.configure_process(config_dict)
        logging.debug('%s: %s constructed', self.__class__.__name__, self._name)

    def do_work(self):

        # Use asset dummy dictonaries to clarify the process code.
        inverter = {}
        inverter.update({key.param_name: val for key, val in self._output.items()})
        grid = {}
        grid.update({key.param_name: val for key, val in self.input.items()})

        # process code
        if grid['kw'] < 0 and abs(grid['kw']) > grid['kw_export_limit']:
            inverter['kw_setpoint'] = grid['kw_export_limit'] + grid['kw']

        elif grid['kw'] > grid['kw_import_limit']:
            inverter['kw_setpoint'] = grid['kw'] - grid['kw_import_limit']
        else:
            inverter['kw_setpoint'] = 0

        # push update asset values to the update dict
        self._output.update({tag: inverter[tag.param_name] for tag in self._output.keys()})

    def __del__(self):
        pass
        # logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)


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
        # logging.debug('%s: %s deconstructed', self.__class__.__name__, self.name)
