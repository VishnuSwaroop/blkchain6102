import sys
from NodeServer import *

class CndsNodeTest(NodeServer):
    def __init__(self, cnds_info):
        self.local_info = cnds_info
        NodeServer.__init__(self, self.local_info)
        print("CNDS listening for connections on {0}".format(self.local_info))
        
    def run(self):
        self.reactor.run()
    
    def handle_get(self, fcn, payload_dict, client_info):
        print("Function [{0}] from {1} Payload: {2}".format(fcn, client_info, str(payload_dict)))
        resp_dict = None
        
        # Create bogus nodes
        node1 = NodeInfo("node1", "localhost", 1235, None, None)
        node2 = NodeInfo("node2", "localhost", 1236, None, None)
        
        network_info = { node1.name: node1, node2.name: node2 }
        
        if fcn == "node":
            print("Responding to node info request")
            resp_dict = node1.get_dict()
            print("Sent node info: " + str(resp_dict))
        elif fcn == "network":
            print("Responding to network info request")
            resp_dict = CndsNodeTest.get_network_info_dicts(network_info)
            print("Sent network info: " + str(resp_dict))
            
        return resp_dict
    
    @staticmethod
    def get_network_info_dicts(network_info):
        network_info_dicts = { }
        for name, node in network_info.iteritems():
            network_info_dicts[name] = node.get_dict()
        return network_info_dicts
        
    def handle_post(self, fcn, payload_dict, client_info):
        print("Function [{0}] from {1} Payload: {2}".format(fcn, client_info, str(payload_dict)))
        resp_dict = None
        if fcn == "join":
            resp_dict = self.handle_join(payload_dict, client_info)
            
        return resp_dict
    
    def handle_join(self, payload_dict, client_info):
        print("Responding to join request from {0}".format(client_info))
        resp_dict = { "status": "approved" }
        return resp_dict

def main(args):
    cnds_info_path = None
    cnds_info = NodeInfo("leader1", "localhost", 1234)
    
    # Parse command line arguments
    for arg in args[1:]:
        cnds_info_path = arg
    
    # Load CNDS configuration
    if cnds_info_path:
        cnds_info = load_node_config(cnds_info_path)
    
    # Run server
    print("Starting CNDS node service")
    node = CndsNodeTest(cnds_info)
    node.run()

if __name__ == "__main__":
    main(sys.argv)