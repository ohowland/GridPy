#!/usr/bin/env python3

from GridPi.lib.models import model_core
from GridPi.lib.process import process_core
from GridPi.lib.dispatch import dispatch_core


class System(object):
    """System object holds all data that defines a a system process loop.
    :param self._assets: Asset objects that define physical objects in the power system
           self._modules: Dispatch process modules, either control and analytic, these modules manipulate tagbus data
    """

    def __init__(self):
        self._asset_container = model_core.AssetContainer()
        self._process_container = process_core.ProcessContainer()
        self._state_machine = dispatch_core.DispatchStateMachine(dispatch_core.blackout_state)

    @property
    def asset_container(self):
        return self._asset_container

    @property
    def process_container(self):
        return self._process_container

    @property
    def state_machine(self):
        return self._state_machine

    def add_asset(self, new_asset):
        self._asset_container.add_asset(new_asset)

    def add_process(self, new_process):
        self._process_container.add_process(new_process)

    def run_processes(self):
        self._process_container.run_all(self._asset_container.get_asset)  # 1. passing the get_assets() method only

    def run_state_machine(self):
        self._state_machine.run_all(self._asset_container)  # 2. passing the entire asset_container class
