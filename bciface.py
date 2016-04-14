from twisted.internet import protocol, reactor

class ValidateNode:
	def __init__(self):
		self.connections = { }
		print("ValidateNode initialized")

	def start(self, port):
		print("Starting validating node service")
		reactor.listenTCP(port, ValidateNodeIfaceFactory(self))
		reactor.run()

	def addConnection(self, addr, protocol):
		self.connections[addr] = protocol

	def removeConnection(self, addr):
		self.connections[addr] = None

class ValidateNodeIface(protocol.Protocol):
	def __init__(self, addr, validateNode):
		self.validateNode = validateNode
		self.validateNode.addConnection(addr, self)
		print("ValidateNodeIface initialized")

	# Override this function in derived classes
	# Returns data to be sent or None
	def handleConnect(self, remoteIp):
		print("Handling connection from " + remoteIp)
		return "Hello " + remoteIp

	# Override this function in derived classes
	def handleConnectClosed(self, reason):
		print("Handling connection closed")

	# Override this function in derived classes
	# Returns data to be sent or None
	def handleDataReceived(self, data):
		print("Handling data received: " + data)
		return data

	def connectionMade(self):
		remoteIp = self.transport.getPeer().host
		print("Connection accepted from " + remoteIp)
		retData = self.handleConnect(remoteIp)
		if retData:
			self.transport.write(data)

	def connectionLost(self, reason):
		print("Connection closed: " + reason)
		self.handleConnectClosed(reason)
		self.validateNode.removeConnection(self.addr)

	def dataReceived(self, data):
		print("Received: " + data)
		retData = self.handleDataReceived(data)
		if retData:
			self.transport.write(retData)

class ValidateNodeIfaceFactory(protocol.Factory):
	def __init__(self, validateNode):
		self.validateNode = validateNode
		print("ValidateNodeIfaceFactory initialized")
		
	def buildProtocol(self, addr):
		print("Building ValidateNodeIface protocol")
		return ValidateNodeIface(addr, self.validateNode)
		

