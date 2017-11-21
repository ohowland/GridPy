class StorageFactory(object):
    """Asset factor for the creating of Asset concrete objects

    """
    def __init__(self, module_name):

        self.module_name = module_name

    def factory(self, class_type):
        """ Factory function for Asset Class objects

        :param config_dict: Configuration dictonary
        :return factory_class: Process Class decendent of type listed in config_dict
        """

        new_module = __import__(self.module_name)
        new_pclass = getattr(new_module , class_type)
        new_class = getattr(new_pclass, class_type)
        return new_class()

class DBInterface(object):
    def __init__(self):
        pass

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