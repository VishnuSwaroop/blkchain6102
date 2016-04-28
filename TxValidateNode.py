import sys
from NodeServer import *
from NodeClient import *

class TxValidateNode(NodeServer):
    def __init__(self, cnds_ip, cnds_port, local_ip, local_port):
        NodeServer.__init__(self, local_ip, local_port)
        print("Node listening for connections on " + addr_port_to_str(self.local_ip, self.local_port))
        self.request_network_info(cnds_ip, cnds_port)
        
    def run(self):
        self.reactor.run()
        
    def request_network_info(self, cnds_ip, cnds_port):
        req_dict = { "get_nodes": True }
        NodeClient.create_request(cnds_ip, cnds_port, "GET", "nodes", req_dict, self.handle_network_info_resp)
    
    def handle_network_info_resp(self, payload_dict, fail):
        if not fail:
            self.network_info = payload_dict
            print("Network info retrieved: " + str(self.network_info))
        else:
            raise Exception("Failed to get network info: " + str(fail))
    
    def handle_get(self, fcn, payload_dict):
        print("Function [" + fcn + "] Payload: " + str(payload_dict))
        resp_dict = None
        if fcn == "block":
            resp_dict = self.handle_block_lookup(payload_dict)
            
        return resp_dict
        
    def handle_post(self, fcn, payload_dict):
        print("Function [" + fcn + "] Payload: " + str(payload_dict))
        resp_dict = None
        if fcn == "add_tx":
            resp_dict = self.handle_add_tx(payload_dict)
        elif fcn == "new_tx":
            resp_dict = self.handle_new_tx(payload_dict)
        elif fcn == "block":
            resp_dict = self.handle_add_block(payload_dict)
            
        return resp_dict
    
    def handle_new_tx(self, tx):
        print("Adding transaction (origin)")
        # TODO: validate transaction
        # TODO: add to unconfirmed pool (uc)
        # TODO: if uc overflows, begin working on proof of work (in separate thread?)
        # TODO: if add block received before finishing proof of work, abort, prune uc, and await more transactions
        self.broadcast_message("POST", "add_tx", tx)
        return { "status": "ok" }
    
    def handle_add_tx(self, tx):
        print("Adding transaction")
        # TODO: validate transaction
        # TODO: add to unconfirmed pool (uc)
        # TODO: if uc overflows, begin working on proof of work (in separate thread?)
        # TODO: if add block received before finishing proof of work, abort, prune uc, and await more transactions
        return { "status": "ok" }
    
    def handle_add_block(self, block):
        # TODO: validate block
        # TODO: validate transactions
        self.broadcast_message("POST", "block", block)
        return { "status": "ok" }
    
    def broadcast_message(self, method, fcn, msg_dict):
        print("Broadcasting message: {0} [{1}] {2}".format(method, fcn, str(msg_dict)))
        for node_name, node_info in self.network_info.iteritems():
            ip = node_info["node_ip"]
            port = node_info["node_port"]
            if not (ip == self.local_ip and port == self.local_port):
                print("Broadcasting to " + addr_port_to_str(ip, port))
                NodeClient.create_request(ip, port, method, fcn, msg_dict, None)
    
    def handle_broadcast_resp(self, resp_dict, fail):
        # TODO: remove nodes that do not respond from the list after some number of failed attempts
        pass
    

def main(args):
    cnds_ip = "localhost"
    cnds_port = 1234
    local_ip = "localhost"
    local_port = 1235
    
    # Parse command line arguments
    for arg in args[1:]:
        if arg.isdigit():
            local_port = int(arg)
        else:
            print("Unknown argument: ", arg)
    
    # Run server
    print("Starting Transaction Validation Node service")
    node = TxValidateNode(cnds_ip, cnds_port, local_port, local_ip)
    node.run()

if __name__ == "__main__":
    main(sys.argv)