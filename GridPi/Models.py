class Asset(object):
    """Basic asset in power system.
       All physical devices in the system are considered 'Asset' objects
    """
    def __init__(self):

        # Asset Configuration:
        self.process_name = None
        self.freq_rated = 0.0
        self.volt_rated = 0.0
        self.cap_kva_rated = 0.0
        self.cap_kw_pos_rated = 0.0
        self.cap_kw_neg_rated = 0.0
        self.cap_kvar_pos_rated = 0.0
        self.cap_kvar_neg_rated = 0.0
        self.comm_interface = None # Communications Interface Object

        # Asset Status
        self.freq = 0.0
        self.volt = 0.0
        self.kw = 0.0
        self.kvar = 0.0
        self.cap_kw_pos_avail = 0.0
        self.cap_kw_neg_avail = 0.0
        self.cap_kvar_pos_avail = 0.0
        self.cap_kvar_neg_avail = 0.0
        self.alarm = False
        self.warning = False
        self.caution = False
        self.online = False
        self.on_system = False

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
        self.enabled = False
        self.remote_ctrl = False

        # CtrlAsset Control
        self.enable = False
        self.run = False
        self.clear_faults = False

    def update(self):

        super(CtrlAsset, self).update()

        self.cap_kw_pos_avail = self.cap_kw_pos_rated * self.enabled
        self.cap_kw_neg_avail = self.cap_kw_neg_rated * self.enabled
        self.cap_kvar_pos_avail = self.cap_kvar_pos_rated * self.enabled
        self.cap_kvar_neg_avail = self.cap_kvar_neg_rated * self.enabled


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