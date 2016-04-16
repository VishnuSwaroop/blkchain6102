from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

class NodeServer:
    def __init__(self, localAddr, localPort, backlog):
        endpoint = TCP4ServerEndpoint(reactor, localPort, backlog, localAddr)
        endpoint.listen(NodeServerFactory(self))
        print("Listening for connections on " + localAddr + ":" + str(localPort))
       
    def connectionMade(self, addr):
        print("Connected to: " + addr.host + ":" + str(addr.port))
        
    def connectionLost(self, reason):
        print("Connection lost: " + str(reason))
       
    def dataReceived(self, data):
        print("Received: " + data)
        return data
       
class NodeServerProtocol(Protocol):
    def __init__(self, addr, nodeServer):
        self.addr = addr
        self.nodeServer = nodeServer
    
    def dataReceived(self, data):
        retData = self.nodeServer.dataReceived(data)
        if retData:
            self.transport.write(retData)
        
    def connectionMade(self):
        retData = self.nodeServer.connectionMade(self.addr)
        if retData:
            self.transport.write(retData)
        
    def connectionLost(self, reason):
        self.nodeServer.connectionLost(reason)
        
class NodeServerFactory(Factory):
    def __init__(self, nodeServer):
        self.nodeServer = nodeServer

    def buildProtocol(self, addr):
        return NodeServerProtocol(addr, self.nodeServer)
        