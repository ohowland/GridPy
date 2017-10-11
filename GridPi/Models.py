class AssetFactory(object):
    """Asset factor for the creating of Asset concrete objects

    """
    def __init__(self):
        self.assets_localpath = 'Assets'

    def factory(self, config_dict):
        """ Factory function for Asset Class objects

        :param config_dict: Configuration dictonary
        :return factory_class: Asset Class decendent of type listed in config_dict
        """
        type = config_dict['model_config']['config_class_name']
        new_module = __import__(self.assets_localpath + '.' + type, fromlist=[type])
        new_class = getattr(new_module, type)
        return new_class(config_dict)

class Asset(object):
    """Basic asset in power system.
       All physical devices in the system are considered 'Asset' objects
    """
    def __init__(self):

        # Asset Configuration:
        self.config_process_name = None
        self.config_class_name = None
        self.config_freq_rated = 0.0
        self.config_volt_rated = 0.0
        self.config_cap_kva_rated = 0.0
        self.config_cap_kw_pos_rated = 0.0
        self.config_cap_kw_neg_rated = 0.0
        self.config_cap_kvar_pos_rated = 0.0
        self.config_cap_kvar_neg_rated = 0.0
        self.config_cap_kva_rated = 0.0
        self.config_comm_interface = None # Communications Interface Object

        # Asset Status
        self.status_freq = 0.0
        self.status_volt = 0.0
        self.status_kw = 0.0
        self.status_kvar = 0.0
        self.status_cap_kw_pos_avail = 0.0
        self.status_cap_kw_neg_avail = 0.0
        self.status_cap_kvar_pos_avail = 0.0
        self.status_cap_kvar_neg_avail = 0.0
        self.status_alarm = False
        self.status_warning = False
        self.status_caution = False
        self.status_online = False
        self.status_on_system = False

    def init_model(self, config_dict):
        for key, value in config_dict['model_config'].items():
            if key in self.__dict__.keys():
                self.__dict__[key] = value

    def update(self):

        for key in self.__dict__.keys():
            if key in self.comm_interface.cvt.keys():
                self.__dict__[key] = self.comm_interface.cvt[key]


class CtrlAsset(Asset):
    """CtrlAsset is an extension of the Asset class.
       These devices can be controlled
    """
    def __init__(self):
        Asset.__init__(self)

        # CtrlAsset Configuration
        # ...

        # CtrlAsset Status
        self.status_enabled = False
        self.status_remote_ctrl = False

        # CtrlAsset Control
        self.ctrl_enable = False
        self.ctrl_run = False
        self.ctrl_clear_faults = False

    def update(self):

        super(CtrlAsset, self).update()

        self.status_cap_kw_pos_avail = self.cap_kw_pos_rated * self.enabled
        self.status_cap_kw_neg_avail = self.cap_kw_neg_rated * self.enabled
        self.status_cap_kvar_pos_avail = self.cap_kvar_pos_rated * self.enabled
        self.status_cap_kvar_neg_avail = self.cap_kvar_neg_rated * self.enabled


class GridIntertie(CtrlAsset):
    """Grid intertie archetype object

    """
    def __init__(self):
        CtrlAsset.__init__(self)

    def update(self):
        super(GridIntertie, self).update()


class EnergyStorage(CtrlAsset):
    """Energy Storage archetype object

    """
    def __init__(self):
        CtrlAsset.__init__(self)

    def update(self):
        super(EnergyStorage, self).update()


class Feeder(CtrlAsset):
    """Feeder archetype object

    """
    def __init__(self):
        CtrlAsset.__init__(self)

    def update(self):
        super(Feeder, self).update()

class Module(object):

    def __init__(self):
        self.module_name = None