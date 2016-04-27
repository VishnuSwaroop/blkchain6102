from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
       
def addrPortToStr(ip, port):
    return ip + ":" + str(port)
    
def addrToStr(addr):
    return addrPortToStr(addr.host, addr.port)
       
class Node:
    def __init__(self):
        self.onConnect = None
        self.onReceive = None
        self.onDisconnect = None
        self.protocol = None
        self.reactor = None
    
    def disconnect(self):
        self.protocol.transport.loseConnection()
    
    def connectionMade(self, addr):
        #print("Node connected to " + addrToStr(addr))
        retData = None
        if self.onConnect:
            retData = self.onConnect(addr, self)
        return retData
        
    def connectionLost(self, addr, reason):
        #print("Node connection lost: " + reason.getErrorMessage())
        if self.onDisconnect:
            self.onDisconnect(addr, reason)
       
    def dataReceived(self, addr, data):
        #print("Node received from " + addrToStr(addr) + ": " + data)
        retData = None
        if self.onReceive:
            retData = self.onReceive(addr, data)
        return retData
        
    def completeSend(self, data):
        if self.protocol:
            return self.protocol.transport.write(data)
        return None
        
    def send(self, data):
        # TODO: change the callback event here
        status = self.reactor.callWhenRunning(self.completeSend, data)
        return status
       
class NodeProtocol(Protocol):
    def __init__(self, addr, node):
        self.addr = addr
        self.node = node
        self.node.protocol = self
    
    def dataReceived(self, data):
        retData = self.node.dataReceived(self.addr, data)
        if retData:
            self.transport.write(retData)
        
    def connectionMade(self):
        retData = self.node.connectionMade(self.addr)
        if retData:
            self.transport.write(retData)
        
    def connectionLost(self, reason):
        self.node.connectionLost(self.addr, reason)

