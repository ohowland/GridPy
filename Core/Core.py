from Core.Models import Asset, Module

class TagBusInterface:

    def __init__(self):
        pass

    def add_tag(self, tag):
        pass

    def read_tag(self, tag):
        pass

    def write_tag(self, tag):
        pass

    def factory(self):
        return TagBus()


class TagBus(TagBusInterface):

    def __init__(self):
        self._tags = dict()

    def add_tag(self, tag):
        self._tags[tag] = None

    def read_tag(self, tag):
        return self._tags[tag]

    def write_tag(self, tag):
        self._tags[tag]


class System(object):

    def __init__(self):
        self._config = {'assets': dict(),
                       'modules': dict(),
                       'tagbus': None
                       }

    def add_asset(self, Asset):
        new_asset = dict()
        new_asset[Asset.config['process_name']] = Asset
        self._config['assets'].update(new_asset)

    def add_module(self, Module):
        new_module = dict()
        new_module[Module.module_name] = Module
        self._config['modules'].update(new_module)

    def write_tagbus(self, TagBus):
        self._config['tagbus'] = TagBus

