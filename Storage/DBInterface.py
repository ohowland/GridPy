class DBInterface(object):
    def __init__(self):
        pass

    def connect(self, db_path):
        pass

    def disconnect(self):
        pass

    def constructSchema(self):
        pass

    def addGroup(self, group_name, *args):
        pass

    def writeParam(self, **kwargs):
        pass

    def readParam(self, **kwargs):
        pass