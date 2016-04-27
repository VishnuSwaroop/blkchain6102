from twisted.internet import reactor

from NodeClient import NodeClient, addrToStr  
from NodeMessage import *
from node_structure import node_methods

class TxOriginNode(node_methods):
    def __init__(self, node_config_path, cnds_info_path):
        node_methods.__init__(self)
        self.load_config(node_config_path, cnds_info_path)
        
        self.reactor = reactor
        self.cnds = NodeClient(self.reactor, self.CNDSip, self.CNDSport)
        self.cnds.onConnect = self.cndsOnConnect
        self.cnds.onReceive = self.cndsDataReceived
        
    def run(self):
        print("Running node service")
        self.reactor.run()
        
    def cndsOnConnect(self, addr, node):
        print("Connected to CNDS at " + addrToStr(addr))
        return self.node_info_req().serialize()
        
    def cndsDataReceived(self, addr, data):
        msg_type, msg = NodeMessage.deserialize(data, self.nodecipher)
        print("Received message from CNDS at " + addrToStr(addr) + " (type " + str(msg_type) + ")")
       
        resp_msg = None
       
        # Call appropriate handler
        if msg_type == NodeMessage.NodeInfoResponse:
            resp_msg = self.handle_node_info_resp(msg)
            self.connectToValidateNode()
            
        if resp_msg:
            return resp_msg.serialize()

    def nodeOnConnect(self, addr, node):
        print("Connected to node at " + addrToStr(addr))
        
        # Send transaction request
        return self.get_transaction_msg()
            
    def nodeOnReceive(self, addr, data):
        msg_type, msg = NodeMessage.deserialize(data, self.nodecipher)
        print("Received message from node at " + addrToStr(addr) + " (type " + str(msg_type) + ")")

        resp_msg = None
        
        if msg_type == NodeMessages.AddTxResponse:
            resp_msg = self.handle_add_tx_resp(msg)
    
        if resp_msg:
            return resp_msg.serialize()
            
    def connectToValidateNode(self):
        if self.network_info:
            # Choose node randomly from list and attempt connection
            # TODO: if connect fails, try to connect to another node
            self.client = NodeClient(self.reactor, nodeip, nodeport)
            self.client.onConnect = self.nodeOnConnect
            self.client.onReceive = self.nodeOnReceive
    
    def get_transaction_msg(self):
        # TODO: add queued transaction
        return NodeMessage(NodeMessages.AddTxRequest, { }, self.cipher)
    
    def handle_add_tx_resp(self, msg):
        # TODO: check response and retry if necessary
        return None



