class Tag(object):
    def __init__(self):
        self.name = None
        self.value = None


class TagBus(object):

    def __init__(self):
        self._tags = dict()

    def add_tag(self, Tag):
        self._tags[Tag.name] = Tag.value

    def read_tag(self, Tag):
        return self._tags[Tag.name]

    def write_tag(self, Tag, val):
        self._tags[Tag.name] = val


class System(object):

    def __init__(self):
        self._config = {'assets': dict(),
                       'modules': dict(),
                       'tagbus': None
                       }


    def add_asset(self, Asset):
        new_asset = dict()
        new_asset[Asset.process_name] = Asset
        self._config['assets'].update(new_asset)

    def add_module(self, Module):
        new_module = dict()
        new_module[Module.module_name] = Module
        self._config['modules'].update(new_module)

    def add_tagbus(self, TagBus):
        self._config['tagbus'] = TagBus

    def register_tags(self):
        for asset in self.config['assets']