import sys
from node_structure import *
from NodeServer import NodeServer
from NodeClient import NodeClient
from twisted.internet import reactor

class TxValidateNode(node_methods):
    def __init__(self, cndsIp, cndsPort, localIp, localPort):
        self.reactor = reactor
        
        self.cnds = NodeClient(self.reactor, cndsIp, cndsPort)
        self.cnds.onConnect = self.cndsOnConnect
        self.cnds.onReceive = self.cndsDataReceived
        
        self.server = NodeServer(self.reactor, localIp, localPort, 10)
        self.server.onConnect = self.nodeOnConnect
        self.server.onReceive = self.nodeOnReceive
        
        self.pingCount = 0
        
    def run(self):
        self.reactor.run()
        
    def cndsOnConnect(self, node, addr):
        return self.join_req()
        
    def cndsDataReceived(self, addr, data):
        msg = self.
        if data == "approved":
            self.connection_status(True)
        elif data == "hello?":
            print("Pinged by CNDS")
            self.pingCount += 1
            return "hello"
        else:
            print("Join failed")
            
        return None

    def nodeOnConnect(self, node, addr):
        print("Connected to node at " + addrToStr(addr))
            
    def nodeOnReceive(self, addr, data):
        print("Received from node at " + addrToStr(addr) + ": " + data)

def main(args):
    cndsIp = "localhost"
    cndsPort = 1234
    localIp = "localhost"
    localPort = 1235
    
    numArgs = len(args)
    if numArgs == 5:
        cndsIp = args[1]
        cndsPort = int(args[2])
        localIp = args[3]
        localPort = int(args[4])
    
    print("Starting NodeTest")
    node = TxValidateNode(cndsIp, cndsPort, localIp, localPort)
    node.createnode(localIp, cndsIp)
    node.run()
    
if __name__ == "__main__":
    main(sys.argv)
    
    
    
    




