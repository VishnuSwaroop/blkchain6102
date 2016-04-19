from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

class EchoServer(Protocol):
    def __init__(self, addr):
        self.addr = addr

    def connectionMade(self):
        print("Connection made to " + self.addr.host)
        
    def connectionLost(self, reason):
        print("Connection lost")

    def dataReceived(self, data):
        self.transport.write(data)
        print("Received: " + data)

class EchoFactory(Factory):
    def buildProtocol(self, addr):
        return EchoServer(addr)

endpoint = TCP4ServerEndpoint(reactor, 1234)
endpoint.listen(EchoFactory())
reactor.run()