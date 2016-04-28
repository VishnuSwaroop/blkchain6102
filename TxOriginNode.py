from NodeClient import *
    
class TxOriginNode:
    def __init__(self, cnds_ip, cnds_port, tx):
        self.node_ip = None
        self.node_port = None
        self.node_pubkey = None
        
        self.cnds_ip = cnds_ip
        self.cnds_port = cnds_port
        self.tx = tx
        
        self.get_node_info()
        
    def start(self):
        NodeClient.run()
        
    def get_node_info(self):
        print("Retrieving node info from CNDS")
        NodeClient.create_request(self.cnds_ip, self.cnds_port, 'GET', "node", { "get_node_info": True }, self.handle_node_info_resp)
        
    def handle_node_info_resp(self, resp_dict, fail):
        if not fail:
            # TODO: do some validation here
            self.node_ip = resp_dict["node_ip"]
            self.node_port = resp_dict["node_port"]
            self.node_pubkey = resp_dict["node_pubkey"]
            print("TxValidateNode to contact is at {0}:{1}".format(self.node_ip, self.node_port))
            
            # Send transaction if this succeeds
            if self.tx:
                self.new_tx(self.tx)
        else:    
            raise Exception("Failed to get node info: " + str(fail))
        
    def new_tx(self, tx):
        print("Sending transaction: " + str(tx))
        NodeClient.create_request(self.node_ip, self.node_port, 'POST', "new_tx", tx, self.handle_new_tx_resp)
        
    def handle_new_tx_resp(self, resp_dict, fail):
        if not fail:
            # TODO: do some validation here
            status = resp_dict["status"]
            
            if status == "ok":
                print("Transaction successfully added")
            else:
                raise Exception("Transaction was rejected: " + str(status))
        else:    
            raise Exception("Failed to get node info: " + str(fail))
        
import sys
# from TxOriginNode import *

def main(args):
    cnds_ip = "localhost"
    cnds_port = 1234
    
    # Parse command line arguments
    for arg in args[1:]:
        if arg.isdigit():
            cnds_port = int(arg)
        else:
            cnds_ip = str(arg)
    
    # Run server
    print("Starting Node")
    # try:
    tx = { "newtx": "mytxinfo" }
    node = TxOriginNode(cnds_ip, cnds_port, tx)
    node.start()
    # except Exception as exc:
    #   print("Fatal Error: " + str(exc))

if __name__ == "__main__":
    main(sys.argv)