import sys
from NodeServer import NodeServer, addrToStr
from twisted.internet import reactor

class NodeEntry:
    def __init__(self, node):
        self.node = node
        self.pingNum = 0
        self.pingResp = 0

class CndsTest:
    def __init__(self, localIp, localPort):
        self.reactor = reactor
        self.nodes = { }
        self.server = NodeServer(self.reactor, localIp, localPort, 10)
        self.server.onConnect = self.nodeConnect
        self.server.onReceive = self.nodeReceived
        self.server.onDisconnect = self.nodeDisconnect
    
    def addNode(self, addr, node):
        if addr not in self.nodes:
            self.nodes[addr] = NodeEntry(node)
    
    def removeNode(self, addr):
        if addr in self.nodes:
            del self.nodes[addr]
            
    def joinNode(self, addr):
        print("CNDS: Node joined from " + addrToStr(addr))
        self.setupPing(addr)
        self.nodes[addr].pingNum = 0
        self.nodes[addr].pingResp = 0
        
    def setupPing(self, addr):
        self.reactor.callLater(5, self.pingNode, addr)
        
    def pingNode(self, addr):
        if addr in self.nodes:
            if self.nodes[addr].pingResp == self.nodes[addr].pingNum:
                print("CNDS: Pinging " + addrToStr(addr))
                self.nodes[addr].pingNum += 1
                self.nodes[addr].node.send("hello?")
                self.setupPing(addr)    # schedule next ping
            else:
                print("CNDS: Node at " + addrToStr(addr) + " did not respond to ping in time")
                self.nodes[addr].node.disconnect()
                self.removeNode(addr)
            
    def handlePingResp(self, addr):
        print("CNDS: Node at " + addrToStr(addr) + " responded to ping")
        if addr in self.nodes:
            self.nodes[addr].pingResp += 1
    
    def nodeConnect(self, addr, node):
        print("CNDS: Node connected from " + addrToStr(addr))
        self.addNode(addr, node)
    
    def nodeReceived(self, addr, data):
        #print("CNDS: Received from " + addrToStr(addr) + ": " + data)
        if data == "join":
            self.joinNode(addr)
            return "approved"
        elif data == "hello":
            self.handlePingResp(addr)
        else:
            print("CNDS: Invalid message received from " + addrToStr(addr) + ": " + data)
            return "nack"
            
    def nodeDisconnect(self, addr, reason):
        print("CNDS: Lost connection with " + addrToStr(addr) + ": " + reason.getErrorMessage())
        self.removeNode(addr)

def main(args):
    cndsIp = "localhost"
    cndsPort = 1234
    
    numArgs = len(args)
    if numArgs == 2:
        cndsPort = int(args[1])

    print("Starting CNDS dummy server")
    cndsServer = CndsTest(cndsIp, cndsPort)
    reactor.run()
    
if __name__ == "__main__":
    main(sys.argv)    
    