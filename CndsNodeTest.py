import sys
from NodeServer import *

class CndsNodeTest(NodeServer):
    def __init__(self, cnds_info):
        local_ip = cnds_info["CNDSip"]
        local_port = cnds_info["CNDSport"]
        NodeServer.__init__(self, local_ip, local_port)
        print("CNDS listening for connections on " + addr_port_to_str(local_ip, local_port))
        
    def run(self):
        self.reactor.run()
    
    def handle_get(self, fcn, payload_dict, client_ip):
        print("Function [{0}] from {1} Payload: {2}".format(fcn, client_ip, str(payload_dict)))
        resp_dict = None
        if fcn == "node":
            print("Responding to node info request")
            resp_dict = { "node_ip": "localhost", "node_port": "1235", "node_pubkey": "None" }
            print("Sent node info: " + str(resp_dict))
        elif fcn == "network":
            print("Responding to network info request")
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
        
    def handle_post(self, fcn, payload_dict, client_ip):
        print("Function [{0}] from {1} Payload: {2}".format(fcn, client_ip, str(payload_dict)))
        resp_dict = None
        if fcn == "join":
            resp_dict = self.handle_join(payload_dict)
            
        return resp_dict
    
    def handle_join(self, payload_dict):
        print("Responding to join request")
        resp_dict = { "status": "approved" }
        return resp_dict

def main(args):
    cnds_info_path = None
    cnds_info = {
        "CNDSdomname": "leader1",
        "CNDSip": "localhost",
        "CNDSport": 1234,
        "CNDSpubkey": None
    }
    
    # Parse command line arguments
    for arg in args[1:]:
        cnds_info_path = arg
    
    # Load CNDS configuration
    if cnds_info_path:
        cnds_info = load_cnds_config(cnds_info_path)
    
    # Run server
    print("Starting CNDS node service")
    node = CndsNodeTest(cnds_info)
    node.run()

if __name__ == "__main__":
    main(sys.argv)