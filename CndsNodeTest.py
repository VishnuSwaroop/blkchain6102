import sys
from NodeServer import *

class CndsNodeTest(NodeServer):
    def __init__(self, local_port, local_ip):
        NodeServer.__init__(self, local_port, local_ip)
        print("CNDS listening for connections on " + addr_port_to_str(self.local_ip, self.local_port))
        
    def run(self):
        self.reactor.run()
    
    def handle_get(self, fcn, payload_dict):
        print("Function [" + fcn + "] Payload: " + str(payload_dict))
        resp_dict = None
        if fcn == "node":
            resp_dict = { "node_ip": "localhost", "node_port": "1235", "node_pubkey": "None" }
            print("Sent node info: " + str(resp_dict))
        elif fcn == "nodes":
            resp_dict = {
                "node1": {
                    "node_ip": "localhost",
                    "node_port": 1235,
                    "node_pubkey": None,
                },
                "node2": {
                    "node_ip": "localhost",
                    "node_port": 1236,
                    "node_pubkey": None,
                }
            }
            print("Sent network info: " + str(resp_dict))
            
        return resp_dict
        
    def handle_post(self, fcn, payload_dict):
        print("Function [" + fcn + "] Payload: " + str(payload_dict))
        resp_dict = None
        if fcn == "join":
            resp_dict = self.handle_join(payload_dict)
            
        return resp_dict

def main(args):
    local_ip = "localhost"
    local_port = 1234
    
    # Parse command line arguments
    for arg in args[1:]:
        if arg.isdigit():
            local_port = int(arg)
        else:
            print("Unknown argument: ", arg)
    
    # Run server
    print("Starting CNDS node service")
    node = CndsNodeTest(local_port, local_ip)
    node.run()

if __name__ == "__main__":
    main(sys.argv)