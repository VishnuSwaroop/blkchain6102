from twisted.internet import reactor

from NodeServer import NodeServer, addrToStr
from NodeClient import NodeClient    
from NodeMessage import *
from node_structure import node_methods

class TxValidateNode(node_methods):
    def __init__(self, cndsIp, cndsPort, localIp, localPort):
        node_methods.__init__(self)
        
        self.reactor = reactor
        self.cnds = NodeClient(self.reactor, cndsIp, cndsPort)
        self.cnds.onConnect = self.cndsOnConnect
        self.cnds.onReceive = self.cndsDataReceived
        
        self.server = NodeServer(self.reactor, localIp, localPort, 10)
        self.server.onConnect = self.nodeOnConnect
        self.server.onReceive = self.nodeOnReceive
        
    def run(self):
        print("Running node service")
        self.reactor.run()
        
    def cndsOnConnect(self, addr, node):
        print("Connected to CNDS at " + addrToStr(addr))
        return self.join_req().serialize()
        
    def cndsDataReceived(self, addr, data):
        msg_type, msg = NodeMessage.deserialize(data, self.nodecipher)
        print("Received message from CNDS at " + addrToStr(addr) + " (type " + str(msg_type) + ")")
        
        if msg_type == NodeMessages.JoinResponse:
            self.handle_join_resp(msg)
        elif msg_type == NodeMessages.PingRequest:
            return self.handle_ping_req(msg).serialize()
            
        return None

    def nodeOnConnect(self, addr, node):
        print("Connected to node at " + addrToStr(addr))
            
    def nodeOnReceive(self, addr, data):
        print("Received message from node at " + addrToStr(addr))

    
    
    




