#!/usr/bin/env python3

import logging

from GridPi.lib.process import process_graph
from collections import namedtuple

class ProcessFactory(object):
    """Asset factor for the creating of Asset concrete objects

    """

    def __init__(self):
        self.module_name = self.__module__.split('.')[0]

    def factory(self, configparser):
        """ Factory function for Asset Class objects

        :param config_dict: Configuration dictonary
        :return factory_class: process Class decendent of type listed in config_dict
        """
        class_type = configparser['class_name']
        new_module = __import__(self.module_name + '.lib.process.' + 'process_plugins', fromlist=[type])
        # new_pclass = getattr(new_module , 'process')
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
        temp_graph = process_graph.GraphProcess(self)  # Note that self IS a ProcessContainer.
        temp_graph.build_adj_list()
        process_names_topo_sort = process_graph.DFS(temp_graph).topological_sort

        self._process_list = []
        for process_name in process_names_topo_sort:
            logging.debug('PROCESS CONTAINER: sort(): New process added to process_list %s',
                          self.process_dict[process_name])
            self._process_list.append(self.process_dict[process_name])
        logging.debug('PROCESS CONTAINER: sort(): final process_list %s', self.process_list)

        self._ready = True

    def run_all(self, get_asset_func):
        """ Run all processes in container
        """
        logging.debug('PROCESS CONTAINER: Running the following processes %s', self.process_list)
        if self._ready:
            for process in self._process_list:
                process.run(get_asset_func)
        else:
            logging.debug('process module not ready, please run self.sort()')


class ProcessInterface(object):
    def __init__(self):
        self._input = dict()
        self._output = dict()
        self._config = dict()
        self._name = 'UNDEFINED'
        self.tag = namedtuple('tag', 'asset_type, id, cat, param_name')

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

    def configure_process(self, config_dict):
        for key, val in config_dict.items():
            if key in self.config.keys():
                if isint(val):
                    val = int(val)
                elif isfloat(val):
                    val = float(val)
                self.config[key] = val

    def run(self, get_asset_func):
        self.read_input(get_asset_func)
        try:
            self.do_work()
        except TypeError as e:
            logging.info('%s: do_work() returned exception: %s', self.__class__.__name__, e)

        self.write_output(get_asset_func)

    def read_input(self, get_asset_func):
        '''

        :param get_asset_func(asset_subclass): this function must return a list of assets of a specified sub-class
        :return:
        '''
        ret = dict() # returned dictonary {namedtuple self.tag, list(value)}
        for tag in self.input.keys():
            if tag.cat == 'status':
                # Return a list of status parameter values
                ret.update({tag: x.status[tag.param_name] for x in get_asset_func(tag.asset_type)})

            if tag.cat == 'control':
                # Return a list of control parameter values
                ret.update({tag: x.control[tag.param_name] for x in get_asset_func(tag.asset_type)})

            if tag.cat == 'config':
                # Return a list of configuration parameter values
                ret.update({tag: x.config[tag.param_name] for x in get_asset_func(tag.asset_type)})
        return ret

    def write_output(self, get_asset_func):
        for tag, val in self.output.items():
            # Set the value of the tag in the asset of specified id.
            getattr(get_asset_func(tag.asset_type)[tag.id], tag.cat)[tag.param_name] = val

    def do_work(self):
        pass


class SingleProcess(ProcessInterface):
    def __init__(self):
        super(SingleProcess, self).__init__()


class AggregateProcess(ProcessInterface):
    def __init__(self, process_list):
        super(AggregateProcess, self).__init__()

        self._process_list = process_list

        for process in self._process_list:
            self._input.update(process._input)

    def run(self, get_asset_func):

        for process in self._process_list:
            process.read_input(get_asset_func)
            try:
                self.do_work()
            except TypeError as e:
                logging.info('%s: do_work() returned exception: %s', self.__class__.__name__, e)
        self.write_output(get_asset_func)


""" HELPERS """


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
