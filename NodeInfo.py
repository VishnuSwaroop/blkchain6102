
class NodeInfo:
    def __init__(self, name=None, ip=None, port=None, pubkey=None):
        self.name = name
        self.ip = ip
        self.port = port
        self.pubkey = pubkey
        
    def get_dict(self):
        return { "name": self.name, "ip": self.ip, "port": self.port, "pubkey": self.pubkey } 
    
    @staticmethod
    def from_dict(d, default_port=80):
        ip = d["ip"]
        port = default_port
        name = None
        pubkey = None
        
        if "name" in d:
            name = d["name"]
            
        if "pubkey" in d:
            pubkey = d["pubkey"]
            
        if "port" in d:
            port = d["port"]
        
        return NodeInfo(name, ip, port, pubkey)
    
    def get_uri(self):
        return "{0}:{1}".format(self.ip, self.port)
    
    def __str__(self):
        return "{0} ({1}:{2})".format(self.name, self.ip, self.port)
    
    def __getitem__(self, key):
        item = None
        if key in self.__dict__:
            item = self.__dict__[key]
        return item
    
    


