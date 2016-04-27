from twisted.internet import reactor

from NodeServer import NodeServer, addrToStr
from NodeClient import NodeClient    
from NodeMessage import *
from node_structure import node_methods

class TxValidateNode(node_methods):
    def __init__(self, node_config_path, cnds_info_path, port_override):
        node_methods.__init__(self)
        self.load_config(node_config_path, cnds_info_path)
        
        # Override port number specified in config file if defined
        if port_override:
            self.nodeport = port_override
        
        self.reactor = reactor
        self.cnds = NodeClient(self.reactor, self.CNDSip, self.CNDSport)
        self.cnds.onConnect = self.cndsOnConnect
        self.cnds.onReceive = self.cndsDataReceived
        
        self.server = NodeServer(self.reactor, self.nodeip, self.nodeport, 10)
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
        
        resp_msg = None
        
        # TODO: check for correct CNDS ip
        
        # Call appropriate handler
        if msg_type == NodeMessages.JoinResponse:
            resp_msg = self.handle_join_resp(msg)
        elif msg_type == NodeMessages.PingRequest:
            resp_msg = self.handle_ping_req(msg)
        elif msg_type == NodeMessages.NodeInfoResponse:
            resp_msg = self.handle_node_info_resp(msg)
            
        if resp_msg:
            return resp_msg.serialize()

    def broadcastMessage(self, msg):
        for addrStr, node_info in self.network_info:
            # TODO: need to check status of connect/send and remove node from node_info table if failed
            client = NodeClient(self.reactor, node_info.ip, node_info.port)
            client.send(msg.serialize())
            
    def nodeOnConnect(self, addr, node):
        print("Connected to node at " + addrToStr(addr))
            
    def nodeOnReceive(self, addr, data):
        msg_type, msg = NodeMessage.deserialize(data, self.nodecipher)
        print("Received message from node at " + addrToStr(addr) + " (type " + str(msg_type) + ")")

        
    
    
    




