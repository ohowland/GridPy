class Asset(object):
    """Basic asset in power system."""

    def __init__(self):

        # Asset Properties:
        self.process_name = str()
        self.freq_rated = int()
        self.volt_rated = int()
        self.cap_kw_pos_rated = int()
        self.cap_kw_neg_rated = int()
        self.cap_kvar_pos_rated = int()
        self.cap_kvar_neg_rated = int()

        # Asset Status:
        self.freq = float()
        self.volt = float()
        self.cap_kw_pos_avail = float()
        self.cap_kw_neg_avail = float()
        self.cap_kvar_pos_avail = float()
        self.cap_kvar_neg_avail = float()

        self.alarm = bool(0)
        self.warning = bool(0)
        self.caution = bool(0)
        self.online = bool(0)
        self.on_system = bool(0)

        # Asset Control

class CtrlAsset(Asset):

    def __init__(self):
        Asset.__init__(self)

        # CtAsset Properties

        # CtAsset Status
        self.enabled = bool(0)
        self.remote_ctrl = bool(0)

        # CtAsset Control
        self.enable = bool(0)
        self.run = bool(0)
        self.clear_faults = bool(0)

class GFAsset(CtrlAsset):

    def __init__(self):
        CtrlAsset.__init__(self)

        self.grid_forming = bool(0)

class Diesel(GFAsset):

    def __init__(self):
        GFAsset.__init__(self)

class BatteryInverter(GFAsset):

    def __init__(self):
        GFAsset.__init__(self)