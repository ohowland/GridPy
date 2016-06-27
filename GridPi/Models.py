class Asset(object):
    """Basic asset in power system.

    """
    def __init__(self):

        # Asset Configuration Dictionary:
        self.config = {'process_name': None,
                       'freq_rated': 0,
                       'volt_rated': 0,
                       'cap_kva_rated': 0,
                       'cap_kw_neg_rated': 0,
                       'cap_kvar_pos_rated': 0,
                       'cap_kvar_neg_rated': 0,
                       'model_type': None
                       }

        # Asset Status Dictionary
        self.status = {'freq': 0.0,
                       'volt': 0.0,
                       'cap_kw_pos_avail': 0.0,
                       'cap_kw_neg_avail': 0.0,
                       'cap_kvar_pos_avail': 0.0,
                       'cap_kvar_neg_avail': 0.0,
                       'alarm': False,
                       'warning': False,
                       'caution': False,
                       'online': False,
                       'on_system': False
                       }

        # Asset Control Dictonary
        self.ctrl = {}

class CtrlAsset(Asset):

    def __init__(self):
        Asset.__init__(self)

        # CtrlAsset Configuration
        self.config.update()

        # CtrlAsset Status
        self.status.update(
            {
                'kw': 0.0,
                'kvar': 0.0,
                'enabled': False,
                'remote_ctrl': False
            }
        )

        # CtrlAsset Control

        self.ctrl.update(
            {
                'enable': False,
                'run': False,
                'clear_faults': False
            }
        )

class GFAsset(CtrlAsset):

    def __init__(self):
        CtrlAsset.__init__(self)

        self.config.update({})

        self.status.update(
            {
                'grid_forming_active': False
            }
        )

        self.ctrl.update(
            {
                'grid_forming_enabled': False
            }
        )

class Diesel(GFAsset):

    def __init__(self):
        GFAsset.__init__(self)

        self.config['model_type'] = 'diesel'

class GridIntertie(GFAsset):

    def __init__(self):
        GFAsset.__init__(self)

        self.config['model_type'] = 'gridintertie'