from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from NodeProtocol import Node
        
class NodeClient(Node):
    def __init__(self, reactor, remoteIp, remotePort):
        Node.__init__(self)
        self.reactor = reactor
        self.connectClient(remoteIp, remotePort)
        
    def connectClient(self, remoteIp, remotePort):
        self.reactor.connectTCP(remoteIp, remotePort, NodeClientFactory(self))
        print("Node connecting to " + addrPortToStr(remoteIp, remotePort))

class NodeClientFactory(ClientFactory):
    def __init__(self, node):
        self.node = node
        
    def buildProtocol(self, addr):
        return NodeProtocol(addr, self.node)