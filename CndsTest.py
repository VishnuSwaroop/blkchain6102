import sys
from twisted.internet import reactor
from NodeServer import NodeServer, addrToStr
from NodeMessage import *

class NodeEntry:
    def __init__(self, node):
        self.node = node
        self.pingNum = 0
        self.pingResp = 0
        self.name = None
        self.ip = None
        self.pubkey = None
        self.cipher = None
        
    def populate(self, name, ip, pubkey):
        self.name = name
        self.ip = ip
        self.pubkey = pubkey
        key = (long(pubkey[0]), long(pubkey[1]))
        self.cipher = PKCS1_OAEP.new(RSA.construct(key))     

class CndsTest:
    def __init__(self, cnds_config_path):
        
        pvtkey = None
        with open(cnds_config_path,'r') as data_file:    
            cnds_config = json.load(data_file)
            key = cnds_config["CNDSpvtkey"]
            pvtkey = (long(key[0]), long(key[1]), long(key[2]))
            localIp = cnds_config["CNDSip"]
            localPort = cnds_config["CNDSport"]
        
        self.reactor = reactor
        self.server = NodeServer(self.reactor, localIp, localPort, 10)
        self.server.onConnect = self.nodeConnect
        self.server.onReceive = self.nodeReceived
        self.server.onDisconnect = self.nodeDisconnect
        self.nodes = { }
        
        # Create cipher
        self.cipher = PKCS1_OAEP.new(RSA.construct(pvtkey))
        
    @staticmethod
    def generateCndsConfig(cnds_config_path, cnds_info_path, cndsip, cndsport):
        CNDSdomname = "leader1"
        print("Creating public and private keys")
        random_generator = Random.new().read
        key1 = RSA.generate(4096, random_generator)
        pvtkey=(long(key1.publickey().n),long(key1.publickey().e),long(key1.d))
        pubkey=(long(key1.publickey().n),long(key1.publickey().e))
        
        # Create cnds_config.json
        cnds_config = {"CNDSip": cndsip,
            "CNDSdomname": CNDSdomname,
            "CNDSport": cndsport,
            "CNDSpubkey": pubkey,
            "CNDSpvtkey": pvtkey}
        
        print("Saving CNDS config")
        with open(cnds_config_path, 'w') as outfile:
            json.dump(cnds_config, outfile, indent=4, sort_keys=True)
            
        # Create cnds_info.json
        cnds_info = {"CNDSip": cndsip,
            "CNDSdomname": CNDSdomname,
            "CNDSport": cndsport,
            "CNDSpubkey": pubkey}
        
        print("Saving CNDS info")
        with open(cnds_info_path, 'w') as outfile:
            json.dump(cnds_info, outfile, indent=4, sort_keys=True)
        
    def run(self):
        print("Running CNDS server")
        self.reactor.run()
    
    def addNode(self, addr, node):
        if addr not in self.nodes:
            self.nodes[addr] = NodeEntry(node)
    
    def removeNode(self, addr):
        if addr in self.nodes:
            del self.nodes[addr]
            
    def joinNode(self, addr, join_msg):
        print("CNDS: Node joined from " + addrToStr(addr))
        self.setupPing(addr)
        self.nodes[addr].populate(join_msg["nodename"], 
            join_msg["nodeip"], join_msg["nodepubkey"])
        return NodeMessage(NodeMessages.JoinResponse, {"approved":True}, self.nodes[addr].cipher)
        
    @staticmethod
    def get_network_info(nodes):
        network_info = { }
        for addr, node in nodes.iteritems():
            network_info[node.name] = {
                "ip": node.ip,
                "port": addr.port,
                "pubkey": node.pubkey,
            }
        return network_info
        
    def setupPing(self, addr):
        pingInterval = 30
        self.reactor.callLater(pingInterval, self.pingNode, addr)
        
    def pingNode(self, addr):
        if addr in self.nodes:
            if self.nodes[addr].pingResp == self.nodes[addr].pingNum:
                print("CNDS: Pinging " + addrToStr(addr))
                self.nodes[addr].pingNum += 1
                msg = NodeMessage(NodeMessages.PingRequest, {"tag":self.nodes[addr].pingNum}, 
                    self.nodes[addr].cipher)
                self.nodes[addr].node.send(msg.serialize())
                self.setupPing(addr)    # schedule next ping
            else:
                print("CNDS: Node at " + addrToStr(addr) + " did not respond to ping in time")
                self.nodes[addr].node.disconnect()
                self.removeNode(addr)
            
    def handlePingResp(self, addr, ping_resp):
        print("CNDS: Node at " + addrToStr(addr) + " responded to ping")
        if addr in self.nodes:
            self.nodes[addr].pingResp = ping_resp["tag"]
    
    def handleNodeInfoRequest(self, addr, info_req):
        print("CNDS: Node at " + addrToStr(addr) + " requesting info")
        return NodeMessage(NodeMessages.NodeInfoResponse, CndsTest.get_network_info(self.nodes), self.cipher)
    
    def nodeConnect(self, addr, node):
        print("CNDS: Node connected from " + addrToStr(addr))
        self.addNode(addr, node)
    
    def nodeReceived(self, addr, data):
        # Lookup addr to get cipher
        msg_type, msg = NodeMessage.deserialize(data, self.cipher)
        print("Received message from node at " + addrToStr(addr) + " (type " + str(msg_type) + ")")
        
        resp_msg = None
        
        if msg_type == NodeMessages.JoinRequest:
            resp_msg = self.joinNode(addr, msg)
        elif msg_type == NodeMessages.PingResponse:
            resp_msg = self.handlePingResp(addr, msg)
        elif msg_type == NodeMessages.NodeInfoRequest:
            resp_msg = self.handleNodeInfoRequest(addr, msg)
        else:
            print("CNDS: Invalid message received from " + addrToStr(addr) + ": " + data)
        
        if resp_msg:
            return resp_msg.serialize()
            
    def nodeDisconnect(self, addr, reason):
        print("CNDS: Lost connection with " + addrToStr(addr) + ": " + reason.getErrorMessage())
        self.removeNode(addr)

def main(args):
    generate = False
    cnds_config_path = "cnds_config.json"
    cnds_info_path = "cnds_info.json"
   
    for arg in args[1:]:
        if arg == "gen":
            generate = True
        else:
            cnds_config_path = arg
        
    # Generate node ID
    if generate:
        print("Generating CNDS configuration")
        CndsTest.generateCndsConfig(cnds_config_path, cnds_info_path, "localhost", 1234)

    print("Starting CNDS server")
    cndsServer = CndsTest(cnds_config_path)
    cndsServer.run()
    
if __name__ == "__main__":
    main(sys.argv)    
    