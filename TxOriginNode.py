import sys
from twisted.web.client import Agent
from twisted.internet import reactor, endpoints
from twisted.web.http_headers import Headers
from twisted.internet.endpoints import TCP4ServerEndpoint
from TxNodeUtil import *

class TxOriginNode(resource.Resource):
    def __init__(self, cnds_ip, node_ip):
        self.reactor = reactor
        self.agent = Agent(self.reactor)
        
    @staticmethod
    def add_tx(self, tx):
        self.res = self.agent.request(
            'POST',
            ')

def main(args):
    cnds_ip = "localhost"
    cnds_port = 1234
    node_ip = "localhost"
    node_port = 1235
    
    # Parse command line arguments
    for arg in args[1:]:
        if arg.isdigit():
            local_port = int(arg)
        else:
            print("Unknown argument: ", arg)
    
    # Run server
    print("Starting Node")
    node = TxValidateNode(cnds_ip, local_port, local_ip)
    node.run()

if __name__ == "__main__":
    main(sys.argv)