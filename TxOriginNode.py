from NodeClient import *
from tx_format import *
    
class TxOriginNode:
    def __init__(self, cnds_info, txs):
        self.reactor = None
        self.node_info = None
        
        self.cnds_info = cnds_info
        
        self.txs = txs
        
        self.get_node_info()
        
    def start(self):
        NodeClient.run()
    
    def get_node_info(self):
        print("Retrieving node info from CNDS")
        NodeClient.create_request(None, self.cnds_info, 'GET', "node", { "get_node_info": True }, self.handle_node_info_resp)
        
    def handle_node_info_resp(self, resp_dict, fail):
        if not fail:
            # TODO: do some validation here
            self.node_info = NodeInfo.from_dict(resp_dict)
            print("TxValidateNode to contact is {0}".format(self.node_info))
            
            # Send transaction if this succeeds
            if self.txs:
                for tx in self.txs:
                    self.send_new_tx(tx)
                    # self.reactor.callLater(1, self.send_new_tx, tx)
        else:    
            raise Exception("Failed to get node info: " + str(fail))
        
    def send_new_tx(self, tx):
        print("Sending transaction: " + str(tx))
        NodeClient.create_request(None, self.node_info, 'POST', "new_tx", tx.to_dict(), self.handle_new_tx_resp)
        
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
    cnds_info = NodeInfo(None, "localhost", 1234)
    
    # Parse command line arguments
    for arg in args[1:]:
        cnds_info_path = arg
    
    # Load CNDS configuration
    if cnds_info_path:
        cnds_info = load_node_config(cnds_info_path)
    
    # Run server
    print("Starting Node")
    # try:
    tx1 = tx_object("localhost", "me", 1, None, None, previous_hash=None)
    tx2 = tx_object("localhost", "me", 2, None, None, previous_hash=tx1.current_hash)
    tx3 = tx_object("localhost", "me", 3, None, None, previous_hash=tx2.current_hash)
    tx4 = tx_object("localhost", "me", 4, None, None, previous_hash=tx3.current_hash)
    tx5 = tx_object("localhost", "me", 5, None, None, previous_hash=tx4.current_hash)
    tx6 = tx_object("localhost", "me", 6, None, None, previous_hash=tx5.current_hash)
    tx7 = tx_object("localhost", "me", 7, None, None, previous_hash=tx6.current_hash)
    tx8 = tx_object("localhost", "me", 8, None, None, previous_hash=tx7.current_hash)
    tx9 = tx_object("localhost", "me", 9, None, None, previous_hash=tx8.current_hash)
    txs = [tx1, tx2, tx3, tx4, tx5, tx6, tx7, tx8, tx9]
    node = TxOriginNode(cnds_info, txs)
    node.start()
    # except Exception as exc:
    #   print("Fatal Error: " + str(exc))

if __name__ == "__main__":
    main(sys.argv)