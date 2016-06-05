Class Asset(object):
    def __init__(self, process_name):
    """self.properties contains data from sys_config.

    """
    # Asset Properties:
    self.process_name = str()
    self.frequency_rated = int()
    self.voltage_rated = int()
    self.cap_kw_pos_rated = int()
    self.cap_kw_neg_rated = int()
    self.cap_kvar_pos_rated = int()
    self.cap_kvar_neg_rated = int()
    
    # Asset Status:
    self.frequency = float()
    self.voltage = float()
    self.cap_kw_pos_avail = float()
    self.cap_kw_neg_avail = float()
    self.cap_kvar_pos_avail = float()
    self.cap_kvar_neg_avail = float()
    
    self.alarm = bool()
    self.warning = bool()
    self.caution = bool()

    # Asset Control
    

Class CtrlAsset(CtAsset)
    def __init__(self):
        CtAsset.__init__(self)

    # CtAsset Properties

    # CtAsset Status
    self.enabled
    self.remote_ctrl_enable

    # CtAsset Control
    self.enable
    self.run
    self.clear_faults

Class Diesel(CtAsset):
    def __init__(self):
        CtAsset.__init__(self)

Class BatteryInverter(CtAsset):
    def __init__(self):
        CtAsset.__init__(self)

Class GridIntertie(CtrlAssetAsset):
    def __init__(self):
        CtrlAssetAsset.__init__(self)
