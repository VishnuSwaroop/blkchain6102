from NodeServer import NodeServer
from twisted.internet import reactor

def main():
    print("Starting CNDS dummy server")
    cndsServer = NodeServer("localhost", 1234, 1)
    reactor.run()
    
if __name__ == "__main__":
    main()    
    