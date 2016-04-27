from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from NodeProtocol import Node, addrToStr, addrPortToStr

class NodeServer(Node):
    def __init__(self, reactor, localIp, localPort, backlog):
        Node.__init__(self)
        self.reactor = reactor
        self.listenForConnect(localIp, localPort, backlog)
        
    def listenForConnect(self, localIp, localPort, backlog):
        endpoint = TCP4ServerEndpoint(self.reactor, localPort, backlog, localIp)
        endpoint.listen(NodeServerFactory(self))
        print("Node listening for connections on " + addrPortToStr(localIp, localPort))
        
class NodeServerFactory(Factory):
    def __init__(self, node):
        self.node = node
        
    def buildProtocol(self, addr):
        return NodeProtocol(addr, self.node)
