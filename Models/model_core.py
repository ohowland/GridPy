#!/usr/bin/env python3
from re import compile, match
import logging

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

class AssetFactory(object):
    """Asset factor for the creating of Asset concrete objects

    """
    def __init__(self):
        self.module_name = self.__module__.split('.')[0]
        pass

    def factory(self, configparser):
        """ Factory function for Asset Class objects

        :param config_dict: Configuration dictonary
        :return factory_class: Asset Class decendent of type listed in config_dict
        """
        class_type = configparser['class_name']
        new_module = __import__(self.module_name + '.' + class_type, fromlist=[type])
        new_class = getattr(new_module, class_type)
        return new_class(configparser)

class AssetContainer(object):
    def __init__(self):

        self._assets = list()
        self._asset_dict = {}

        self._ess = list()
        self._grid = list()
        self._feeder = list()

    def add_asset(self, asset_obj):

        self._assets.append(asset_obj)
        self._asset_dict.update({asset_obj.config['name']: asset_obj})

        # TODO: Remove these lists, pending review.
        if asset_obj.config['class_type'] == 'ess':
            self._ess.append(asset_obj)
        elif asset_obj.config['class_type'] == 'grid':
            self._grid.append(asset_obj)
        elif asset_obj.config['class_type'] == 'feeder':
            self._feeder.append(asset_obj)

    def read(self, args):
        resp = dict()
        for asset_name, type_name, param_name in args:
            try:
                resp.update({(asset_name, type_name, param_name):
                                 getattr(self._asset_dict[asset_name], type_name)[param_name]})
            except KeyError:
                logging.warning('%s: read(): %s does not exists',
                                self.__class__.__name__, (asset_name, type_name, param_name))
        return resp

    def write(self, args):
        for key, val in args.items():
            try:
                asset_name, type_name, param_name = key
                getattr(self._asset_dict[asset_name], type_name)[param_name] = val
            except KeyError:
                logging.warning('%s: write(): %s does not exists', self.__class__.__name__, key)

    @property
    def assets(self):
        return self._assets

    @property
    def ess(self):
        return self._ess

    @property
    def grid(self):
        return self._grid

    @property
    def feeder(self):
        return self._feeder


class Asset(object):
    """Basic asset in power system.
       All physical devices in the system are considered 'Asset' objects
    """
    def __init__(self):

        # Asset Configuration:
        self.config = dict()
        self.status = dict()
        self.control = dict()
        self.comm_interface = None  # Communications Interface Object

        self.config.update({
            'name' : None,
            'class_name': None,
            'class_type': None,
            #  'freq_rated': None,
            #  'volt_rated': None,
            #  'cap_kva_rated': 0.0,
            'cap_kw_pos_rated': 0.0,
            'cap_kw_neg_rated': 0.0,
            #  'cap_kvar_neg_rated': 0.0,
            #  'cap_kvar_pos_rated': 0.0,
        })

        self.status.update({
            'freq': 0.0,
            'volt': 0.0,
            'kw': 0.0,
            'kvar': 0.0,
            #  'cap_kw_pos_avail': 0.0,
            #  'cap_kw_neg_avail': 0.0,
            #  'cap_kvar_pos_avail': 0.0,
            #  'cap_kvar_neg_avail': 0.0,
            'alarm': False,
            #  'warning': False,
            #  'caution': False,
            'online': False
            # ' on_system': False
        })

    def initModel(self, config_dict):
        for key, val in config_dict.items():
            if key in self.config.keys(): # ConfigParser stores all data as string. Attempt to convert to float or int.
                if isint(val):
                    val = int(val)
                elif isfloat(val):
                    val = float(val)
                self.config[key] = val

    def update_status(self):
        """ The update status routine on any asset is as follows:
            1. Update internal dictionary from communications interface
            2. Map internal status dictionary to abstract parent interface
        """
        return

    def update_control(self):
        """ The update control routine on any asset is as follows:
            1. Map the abstract parent inferface to internal control dictionary
            2. Write the communications interface from internal control dictionary.
        """
        return


#        for key in self.__dict__.keys():
#            if key in self.config['comm_interface'].cvt.keys():
#                self.__dict__[key] = self.config['comm_interface'].cvt[key]

class CtrlAsset(Asset):
    """CtrlAsset is an extension of the Asset class.
       These devices can be controlled
    """
    def __init__(self):
        super(CtrlAsset, self).__init__()

        self.internal_status = dict()  # Device Status Registers
        self.internal_control = dict()    # Device Control Registers
        self.internal_config = dict()  # Device Configuration Registers

        # CtrlAsset Configuration
        # ...

        # CtrlAsset Status
        self.status.update({
            'enabled' : False,
            #  'remote_ctrl' : False
        })

        # CtrlAsset Control
        self.control.update({
            'enable' : False,
            'run' : False,
            'clear_faults' : False
        })

    def update_status(self):

        super(CtrlAsset, self).update_status()

        # self.status['cap_kw_pos_avail'] = self.config['cap_kw_pos_rated'] * self.ctrl['enabled']
        # self.status['cap_kw_neg_avail'] = self.config['cap_kw_neg_rated'] * self.ctrl['enabled']
        # self.status['cap_kvar_pos_avail'] = self.config['cap_kvar_pos_rated'] * self.ctrl['enabled']
        # self.status['cap_kvar_neg_avail'] = self.config['cap_kvar_neg_rated'] * self.ctrl['enabled']


class GridIntertie(CtrlAsset):
    """Grid intertie archetype object
    """
    def __init__(self):
        super(GridIntertie, self).__init__()

        self.config.update({
            'kw_export_limit': 0.0,
            'kw_import_limit': 0.0
        })

    def update(self):
        super(GridIntertie, self).update_status()


class EnergyStorage(CtrlAsset):
    """Energy Persistence archetype object
    """
    def __init__(self):
        super(EnergyStorage, self).__init__()
        self.status.update({
            'soc': 0.0,
        })
        self.control.update({
            'kw_setpoint': 0.0
        })

        self.config.update({
            'target_soc': 0.0
        })

    def update(self):
        super(EnergyStorage, self).update_status()


class Feeder(CtrlAsset):
    """Feeder archetype object
    """
    def __init__(self):
        super(Feeder, self).__init__()

    def update(self):
        super(Feeder, self).update_status()