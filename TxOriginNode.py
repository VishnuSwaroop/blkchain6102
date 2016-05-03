from NodeClient import *
from tx_format import *
from encryption_methods import *
from TxValidateNode import TxValidateNode
    
class TxOriginNode:
    def __init__(self, cnds_info, txs):
        self.reactor = None
        self.node_info = None
        
        self.cnds_info = cnds_info
        
        self.txs = txs
        
        self.get_node_info()
    
    def get_node_info(self):
        print("Retrieving node info from CNDS")
        
        resp_dict = get_validating_node()
        
        # Check if resp_dict is a string
        if not isinstance(resp_dict, basestring):
            self.node_info = NodeInfo(resp_dict["node_name"],
                                resp_dict["ip_address"],
                                TxValidateNode.default_port,
                                resp_dict["public_key"])
            print("TxValidateNode to contact is {0}".format(self.node_info))
        else:
            raise Exception("Failed to get validating node info: " + str(resp_dict))
        
        #self.node_info = NodeInfo("node1", "162.243.41.99", 8080)
        
        # Send transaction if this succeeds
        if self.txs:
            for tx in self.txs:
                self.send_new_tx(tx)
        
    def send_new_tx(self, tx):
        print("Sending transaction: " + str(tx))
        resp_dict = NodeClient.send_request(None, self.node_info, 'POST', "new_tx", tx.to_dict())
        status = resp_dict["status"]
        
        if status == "ok":
            print("Transaction successfully added")
        else:
            raise Exception("Transaction was rejected: " + str(status))
        
import sys
# from TxOriginNode import *

def main(args):
    cnds_info_path = None
    cnds_info = NodeInfo(None, "", 1234)
    
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
    # except Exception as exc:
    #   print("Fatal Error: " + str(exc))

if __name__ == "__main__":
    main(sys.argv)