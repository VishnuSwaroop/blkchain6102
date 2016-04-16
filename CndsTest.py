from NodeServer import NodeServer, addrToStr
from twisted.internet import reactor

class CndsTest(NodeServer):
    def __init__(self, reactor, localIp, localPort):
        NodeServer.__init__(self, reactor, localIp, localPort, 10)
    
    def dataReceived(self, addr, data):
        print("CNDS received from " + addrToStr(addr) + ": " + data)
        if data == "join":
            return "approved"
        else:
            return "nack"

def main():
    print("Starting CNDS dummy server")
    cndsServer = CndsTest(reactor, "localhost", 1234)
    reactor.run()
    
if __name__ == "__main__":
    main()    
    