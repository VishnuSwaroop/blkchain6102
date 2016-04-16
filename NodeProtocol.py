from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
       
def addrPortToStr(ip, port):
    return ip + ":" + str(port)
    
def addrToStr(addr):
    return addrPortToStr(addr.host, addr.port)
       
class Node:
    def __init__(self):
        self.onConnect = None
        self.onReceive = None
        self.protocol = None
        self.reactor = None
        
    def connectClient(self, remoteIp, remotePort):
        self.reactor.connectTCP(remoteIp, remotePort, NodeClientFactory(self))
        print("Connecting to " + addrPortToStr(remoteIp, remotePort))
        
    def listenForConnect(self, localIp, localPort, backlog):
        endpoint = TCP4ServerEndpoint(self.reactor, localPort, backlog, localIp)
        endpoint.listen(NodeServerFactory(self))
        print("Listening for connections on " + addrPortToStr(localIp, localPort))
    
    def connectionMade(self, addr):
        print("Connected to " + addrToStr(addr))
        retData = None
        if self.onConnect:
            retData = self.onConnect(addr)
        return retData
        
    def connectionLost(self, reason):
        print("Connection lost: " + reason.getErrorMessage())
       
    def dataReceived(self, addr, data):
        print("Received from " + addrToStr(addr) + ": " + data)
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
        self.node.connectionLost(reason)

class NodeClientFactory(ClientFactory):
    def __init__(self, node):
        self.node = node
        
    def buildProtocol(self, addr):
        return NodeProtocol(addr, self.node)
        
class NodeServerFactory(Factory):
    def __init__(self, node):
        self.node = node
        
    def buildProtocol(self, addr):
        return NodeProtocol(addr, self.node)

