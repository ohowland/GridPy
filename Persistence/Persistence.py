from pathlib import Path

class PersistenceFactory(object):
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
        new_module = __import__(self.module_name + '.' + class_type, fromlist=[type])
        new_class = getattr(new_module, class_type)
        return new_class(configparser)


class DBInterface(object):
    def __init__(self, config_dict):

        self.db_path = Path(*config_dict['local_path'].split('/'))
        self.db_dir = Path(self.db_path.parent)
        self.db_dir.mkdir(exist_ok=True)


    def connect(self, db_path):
        pass

    def disconnect(self):
        pass

    def constructSchema(self):
        pass

    def addGroup(self, group_name, *args):
        pass

    def writeParam(self, **kwargs):
        pass

    def readParam(self, **kwargs):
        pass