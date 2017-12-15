#!/usr/bin/env python3

import statemachine
from Models import Models
from Process import Process


class System(object):
    """System object holds all data that defines a a system process loop.
    :param self._assets: Asset objects that define physical objects in the power system
           self._modules: Dispatch process modules, either control and analytic, these modules manipulate tagbus data
    """
    def __init__(self):
        self._assets = Models.AssetContainer()
        self._process = Process.ProcessContainer()
        self._state_machine = statemachine.StateMachine()

    @property
    def assets(self):
        return self._assets

    @property
    def process(self):
        return self._process

    @property
    def state_machine(self):
        return self._state_machine

    def add_asset(self, new_asset):
        self._assets.add_asset(new_asset)

    def add_process(self, new_process):
        self._process.add_process(new_process)

    def run_processes(self):
        self._process.run_all(self._assets.read, self._assets.write)