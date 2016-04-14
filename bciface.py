from twisted.internet import protocol, reactor

class Test(protocol.Protocol):
	def __init__(self):
		print("Test protocol initialized")

	def connectionMade(self):
		print("Client accepted at " + self.transport.getPeer().host) 
		self.transport.write("hello client")

	def connectionLost(self, reason):
		print("Client disconnected")

	def dataReceived(self, data):
		print("client: " + data)
		self.transport.write("server: " + data)

class TestFactory(protocol.Factory):
	def __init__(self):
		print("Test factory initialized")

	def buildProtocol(self, addr):
		print("Building test protocol")
		return Test()

reactor.listenTCP(1234, TestFactory())
reactor.run()
