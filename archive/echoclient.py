from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

class EchoClient(Protocol):
    def connectionMade(self):
        self.transport.write("Hello server, I am the client!")
    
    def dataReceived(self, data):
        print(data)
        
point = TCP4ClientEndpoint(reactor, "localhost", 1234)
d = connectProtocol(point, EchoClient())
reactor.run()