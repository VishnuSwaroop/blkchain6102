from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
        
class NodeClient:
    def __init__(self, remoteIp, remotePort):
        reactor.connectTCP(remoteIp, remotePort, NodeClientFactory(self))
       
    def connectionMade(self, addr):
        print("Connected to: " + addr.host + ":" + str(addr.port))
        return "hello world"
        
    def connectionLost(self, reason):
        print("Connection lost: " + str(reason))
       
    def dataReceived(self, data):
        print("Received: " + data)
       
class NodeClientProtocol(Protocol):
    def __init__(self, addr, nodeClient):
        self.addr = addr
        self.nodeClient = nodeClient
    
    def dataReceived(self, data):
        retData = self.nodeClient.dataReceived(data)
        if retData:
            self.transport.write(retData)
        
    def connectionMade(self):
        retData = self.nodeClient.connectionMade(self.addr)
        if retData:
            self.transport.write(retData)
        
    def connectionLost(self, reason):
        self.nodeClient.connectionLost(reason)

class NodeClientFactory(ClientFactory):
    def __init__(self, nodeClient):
        self.nodeClient = nodeClient
        
    def buildProtocol(self, addr):
        return NodeClientProtocol(addr, self.nodeClient)

nodeClient = NodeClient("localhost", 1234)
reactor.run()
