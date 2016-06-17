class Asset(object):
    """Basic asset in power system.

    """
    def __init__(self):

        # Asset Properties:
        self.process_name = None
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
        self.alarm = False
        self.warning = False
        self.caution = False
        self.online = False
        self.on_system = False

        # Asset Control


class CtrlAsset(Asset):

    def __init__(self):
        Asset.__init__(self)

        # CtAsset Properties

        # CtAsset Status
        self.kw = float()
        self.kvar = float()
        self.enabled = False
        self.remote_ctrl = False

        # CtAsset Control
        self.enable = False
        self.run = False
        self.clear_faults = False

class GFAsset(CtrlAsset):

    def __init__(self):
        CtrlAsset.__init__(self)

        self.grid_forming = bool(0)

class Diesel(GFAsset):

    def __init__(self):
        GFAsset.__init__(self)