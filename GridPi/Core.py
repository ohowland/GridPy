class TagBus(object):

    def __init__(self):
        self._tags = dict()

    def add_tag(self, tag, init = None):
        self._tags[tag] = init

    def read_tag(self, tag):
        return self._tags[tag]

    def write_tag(self, tag, val):
        self._tags[tag] = val

    def dump(self):
        for key, val in self._tags.items():
            print(key, val)


class System(object):

    def __init__(self):
        self._assets = dict()
        self._modules = dict()
        self._tagbus = None

    def add_asset(self, Asset):
        new_asset = dict()
        new_asset[Asset.process_name] = Asset
        self._assets.update(new_asset)

    def add_module(self, Module):
        new_module = dict()
        new_module[Module.module_name] = Module
        self._modules.update(new_module)

    def add_tagbus(self, TagBus):
        self._tagbus = TagBus

    def register_tags(self):
        """ Registers all private data in the Models with the Tagbus

        :return:
        """
        for asset in self._assets.values():
            for key, val in asset.__dict__.items():
                tag = asset.process_name + '_' + key
                self._tagbus.add_tag(tag, val)


