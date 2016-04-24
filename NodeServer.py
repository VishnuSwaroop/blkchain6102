from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from NodeProtocol import Node, addrToStr, addrPortToStr

class NodeServer(Node):
    def __init__(self, reactor, localIp, localPort, backlog):
        Node.__init__(self)
        self.reactor = reactor
        self.listenForConnect(localIp, localPort, backlog)
        