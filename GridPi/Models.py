Class Asset(object):
    def __init__(self):
    """self.properties contains data from sys_config.

    """
        self.properties = tuple({})
        self.status = dict()
        self.control = dict()
        
Class Diesel(Asset):
    def __init__(self):
        Asset.__init__(self)

Class BatteryInverter(Asset):
    def __init__(self):
        Asset.__init__(self)

Class GridIntertie(Asset):
    def __init__(self):
        Asset.__init__(self)
