from NodeClient import *
    
class TxOriginNode:
    def __init__(self, cnds_info, txs):
        self.reactor = None
        self.node_ip = None
        self.node_port = None
        self.node_pubkey = None
        
        self.cnds_ip = cnds_info["CNDSip"]
        self.cnds_port = cnds_info["CNDSport"]
        
        self.txs = txs
        
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
            if self.txs:
                for tx in self.txs:
                    self.send_new_tx(tx)
                    # self.reactor.callLater(1, self.send_new_tx, tx)
        else:    
            raise Exception("Failed to get node info: " + str(fail))
        
    def send_new_tx(self, tx):
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
    print("Starting Node")
    # try:
    txs = []
    for i in xrange(1, 5*2):
        txs.append({"tx{0}".format(i): "txinfo"})
    node = TxOriginNode(cnds_info, txs)
    node.start()
    # except Exception as exc:
    #   print("Fatal Error: " + str(exc))

if __name__ == "__main__":
    main(sys.argv)