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
        self.cipher = None
        
    def populate(self, name, ip, pubkey):
        self.name = name
        self.ip = ip
        key = (long(pubkey[0]), long(pubkey[1]))
        self.cipher = PKCS1_OAEP.new(RSA.construct(key))

class CndsTest:
    def __init__(self, localIp, localPort, cnds_info_path):
        self.reactor = reactor
        self.server = NodeServer(self.reactor, localIp, localPort, 10)
        self.server.onConnect = self.nodeConnect
        self.server.onReceive = self.nodeReceived
        self.server.onDisconnect = self.nodeDisconnect
        self.nodes = { }
        
        pvtkey = None
        with open(cnds_info_path,'r') as data_file:    
            cnds_info = json.load(data_file)
            key = cnds_info["CNDSpvtkey"]
            pvtkey = (long(key[0]), long(key[1]), long(key[2]))
       
        self.cipher = PKCS1_OAEP.new(RSA.construct(pvtkey))
        
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
        
    def setupPing(self, addr):
        self.reactor.callLater(10, self.pingNode, addr)
        
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
    
    def nodeConnect(self, addr, node):
        print("CNDS: Node connected from " + addrToStr(addr))
        self.addNode(addr, node)
    
    def nodeReceived(self, addr, data):
        # Lookup addr to get cipher
        msg_type, msg = NodeMessage.deserialize(data, self.cipher)
        print("Received message from node at " + addrToStr(addr) + " (type " + str(msg_type) + ")")
        
        if msg_type == NodeMessages.JoinRequest:
            return self.joinNode(addr, msg).serialize()
        elif msg_type == NodeMessages.PingResponse:
            self.handlePingResp(addr, msg)
        else:
            print("CNDS: Invalid message received from " + addrToStr(addr) + ": " + data)
            
    def nodeDisconnect(self, addr, reason):
        print("CNDS: Lost connection with " + addrToStr(addr) + ": " + reason.getErrorMessage())
        self.removeNode(addr)

def main(args):
    cndsIp = "localhost"
    cndsPort = 1234
    
    #numArgs = len(args)
    #if numArgs == 2:
    #    cndsPort = int(args[1])

    print("Starting CNDS dummy server")
    cndsServer = CndsTest(cndsIp, cndsPort, "CNDSpvtkey.json")
    cndsServer.run()
    
if __name__ == "__main__":
    main(sys.argv)    
    