#!/usr/bin/env python3
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

        :param configparser: Configuration dictonary
        :return factory_class: Asset Class decendent of type listed in config_dict
        """
        class_type = configparser['class_name']
        new_module = __import__(self.module_name + '.lib.models.' + class_type, fromlist=[type])
        new_class = getattr(new_module, class_type)
        return new_class(configparser)


class AssetContainer(object):
    def __init__(self):

        self._asset_list = list()
        #self._asset_dict = {}
        self._asset_roster = {}

    @property
    def asset_list(self):
        return self._asset_list

    def add_asset(self, asset_obj):

        self._asset_list.append(asset_obj)
        #self._asset_dict.update({asset_obj.config['name']: asset_obj})

        try:
            self._asset_roster[asset_obj.config['class_type']].append(asset_obj)
        except (TypeError, KeyError):
            self._asset_roster.update({asset_obj.config['class_type']: [asset_obj]})

    def get_asset(self, class_type):
        return self._asset_roster[class_type]

    """
    def read(self, args):
        resp = dict()
        for asset_name, type_name, param_name in args:
            try:
                resp.update(
                    {(asset_name, type_name, param_name): getattr(self._asset_dict[asset_name], type_name)[param_name]})
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
    """

class Asset(object):
    """Basic asset in power system.
       All physical devices in the system are considered 'Asset' objects
    """

    def __init__(self):
        # Asset Configuration:
        self._config = dict()
        self._status = dict()
        self._control = dict()
        self._comm_interface = None  # Communications Interface Object

        self._config.update({
            'name': None,
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

        self._status.update({
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

    @property
    def status(self):
        return self._status

    @property
    def control(self):
        return self._control

    @property
    def config(self):
        return self._config

    def read_config(self, config_dict):
        for key, val in config_dict.items():
            if key in self._config.keys():  # ConfigParser stores all data as string. Attempt to convert to float or int.
                if isint(val):
                    val = int(val)
                elif isfloat(val):
                    val = float(val)
                self._config[key] = val

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


class CtrlAsset(Asset):
    """CtrlAsset is an extension of the Asset class.
       These devices can be controlled
    """

    def __init__(self):
        super(CtrlAsset, self).__init__()

        self.internal_status = dict()  # Device Status Registers
        self.internal_control = dict()  # Device Control Registers
        self.internal_config = dict()  # Device Configuration Registers

        # CtrlAsset Configuration
        # ...

        # CtrlAsset Status
        self._status.update({
            'enabled': False,
            #  'remote_ctrl' : False
        })

        # CtrlAsset Control
        self._control.update({
            'enable': False,
            'run': False,
            'clear_faults': False
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

        self._config.update({
            'class_type': 'grid',
            'kw_export_limit': 0.0,
            'kw_import_limit': 0.0
        })

    def update_status(self):
        super(GridIntertie, self).update_status()


class EnergyStorage(CtrlAsset):
    """Energy persistence archetype object
    """

    def __init__(self):
        super(EnergyStorage, self).__init__()
        self._status.update({
            'soc': 0.0
        })
        self._control.update({
            'kw_setpoint': 0.0
        })

        self._config.update({
            'class_type': 'ess',
            'target_soc': 0.0
        })

    def update_status(self):
        super(EnergyStorage, self).update_status()


class Feeder(CtrlAsset):
    """Feeder archetype object
    """

    def __init__(self):
        super(Feeder, self).__init__()

        self._config.update({
            'class_type': 'feeder'
        })


    def update_status(self):
        super(Feeder, self).update_status()
