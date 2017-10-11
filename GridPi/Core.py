import re
import logging

class Tag(object):

    def __init__(self, name, value=None, units=None):
        self._name = name
        self._value = value
        self._units = units

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def units(self):
        return self._units


class TagBus(object):

    def __init__(self):
        self._tags = dict()

    @property
    def tags(self):
        return self._tags

    def add_tag(self, tag_name, default_value=None, units=None):
        if (self._tags.get(tag_name, False)):  # Statement executes if tag is found
            logging.warning('tagbus.add_tag(): %s attempting to overwrite existing tag')
        else:                                  # Statement executes if tag is not found
            self._tags[tag_name] = Tag(tag_name, value=default_value, units=units)
            #logging.info('tagbus.add_tag(): %s tag added to tagbus', tag_name)


    def read_tag(self, tag_name):
        return self._tags[tag_name].value

    def write_tag(self, tag_name, value):
        if (self._tags.get(tag_name, False)): # Statement executes if tag is found
            self._tags[tag_name].value = value
            #logging.info('tagbus.write_tag(): writing %s', tag_name)
        else:                                 # Statement executes if tag is not found
            logging.warning("tagbus.write_tag(): %s tag does not exist", tag_name)

    def dump(self):
        for key, val in self.tags.items():
            logging.info('tagbus.dump(): %s %s %s', key, val.value, val.units)


class System(object):
    """System object holds all data that defines a a system process loop.
    :param self._assets: Asset objects that define physical objects in the power system
           self._modules: Dispatch process modules, either control and analytic, these modules manipulate tagbus data
           self._tagbus: Assets register status and controls on the tagbus so that dispatch modules access and
                         manipulate data in a controlled way.

    """

    def __init__(self):
        self._assets = dict()
        self._modules = dict()
        self._tagbus = TagBus()

    @property
    def assets(self):
        return self._assets

    @property
    def tagbus(self):
        return self._tagbus

    @property
    def modules(self):
        return self._modules

    def add_asset(self, asset):
        new_asset = dict()
        new_asset[asset.config_process_name] = asset
        self._assets.update(new_asset)
        return

    def add_module(self, process_module):
        new_module = dict()
        new_module[process_module.module_name] = process_module
        self._modules.update(new_module)
        return

    def add_tagbus(self, tagbus):
        self._tagbus = tagbus
        return

    def register_tags(self):
        """ Registers asset status and control parameters with the Tagbus

        """
        for asset in self.assets.values():
            status_re = re.compile('status|ctrl|^config*') # regular expression for filtering out tagbus names
            gen = (key for key in asset.__dict__.keys() if status_re.match(key))
            for key in gen:
                tag_name = '_'.join([asset.config_process_name, key])
                self.tagbus.add_tag(tag_name, default_value=None, units=None)
        return


    def update_tagbus_from_assets(self):
        """ run update_tagbus_from_asset(asset) on all assets registered in the system

        :return:
        """
        for asset in self.assets.values():
            self.update_tagbus_from_asset(asset)
        return

    def update_tagbus_from_asset(self, asset):
        """ Scan read parameters in asset and push that data onto the Tagbus

        :param asset: Asset object reference
        :return:
        """

        status_re = re.compile('status*')  # regular expression for filtering out tagbus names
        for key, val in asset.__dict__.items():
            if status_re.match(key):
                tag_name = '_'.join([asset.config_process_name, key])
                self.tagbus.write_tag(tag_name, val)
        return

    def write_assets_from_tagbus(self):
        """ run update_tagbus_from_asset(asset) on all assets registered in the system

        :return:
        """
        for asset in self.assets.values():
            self.write_asset_from_tagbus(asset)
        return

    def write_asset_from_tagbus(self, asset):
        """ Scan write parameters in asset from Tagbus data

        :param asset: Asset object reference
        :return:
        """
        control_re = re.compile('ctrl*') # regular expression for filtering out tagbus names
        for key, val in asset.__dict__.items():
            if control_re.match(key):
                tag = '_'.join([asset.config_process_name, key])
                asset.__dict__[key] = self.tagbus.read_tag(tag)
        return

    def process_modules(self):
        pass
