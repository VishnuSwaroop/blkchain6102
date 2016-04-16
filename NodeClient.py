from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from NodeProtocol import Node
        
class NodeClient(Node):
    def __init__(self, reactor, remoteIp, remotePort):
        Node.__init__(self)
        self.reactor = reactor
        self.connectClient(remoteIp, remotePort)

