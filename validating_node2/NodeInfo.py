
class NodeInfo:
    def __init__(self, name=None, ip=None, port=None, pubkey=None, pvtkey=None):
        self.name = name
        self.ip = ip
        self.port = port
        self.pubkey = pubkey
        self.pvtkey = pvtkey
        
    def get_dict(self):
        return self.__dict__
    
    @staticmethod
    def from_dict(d):
        ip = d["ip"]
        port = d["port"]
        pubkey = None
        pvtkey = None
        name = None
        
        if "name" in d:
            name = d["name"]
        if "pubkey" in d:
            pubkey = d["pubkey"]
        if "pvtkey" in d:
            pvtkey = d["pvtkey"]
        
        return NodeInfo(name, ip, port, pubkey, pvtkey)
    
    def get_uri(self):
        return "{0}:{1}".format(self.ip, self.port)
    
    def __str__(self):
        return "{0} ({1}:{2})".format(self.name, self.ip, self.port)
    
    def __getitem__(self, key):
        item = None
        if key in self.__dict__:
            item = self.__dict__[key]
        return item
    
    


