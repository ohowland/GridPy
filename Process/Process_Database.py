from Process import Process
import logging
import sqlite3

class WRITE_SQLITE_DB(Process.SingleProcessProxy):
    def __init__(self, config_dict):
        super(WRITE_SQLITE_DB, self).__init__()

        self._name = 'write_sqlite_db'
        self._input = {}  # Empty input, acts as root node

        self._config.update({'asset_ref': None})
        self._output.update({})

        self.initProcess(config_dict)
        logging.debug('PROCESS INTERFACE: %s constructed', self.name)

    def do_work(self):
        pass

    def __del__(self):
        logging.debug('PROCESS INTERFACE: %s deconstructed', self.name)