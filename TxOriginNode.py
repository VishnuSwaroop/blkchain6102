import time
from NodeClient import *
from tx_format import *
from encryption_methods import *
from TxValidateNode import TxValidateNode
    
class TxOriginNode:
    def __init__(self, cnds_info):
        self.reactor = None
        self.node_info = None
        
        self.cnds_info = cnds_info
        
        #self.txs = txs        
        self.get_node_info()
    
    def get_node_info(self):
        real_cnds = True
        if real_cnds:
            print("Retrieving node info from CNDS")
            
            resp_dict = get_validating_node()
            status = resp_dict["status"]
            
            # Check if resp_dict is a string
            if status == "Available":
                self.node_info = NodeInfo(None,
                                    resp_dict["suggested_node"],
                                    TxValidateNode.default_port)
                print("TxValidateNode to contact is {0}".format(self.node_info))
            else:
                raise Exception("Failed to get validating node info: " + str(status))
        else:
        # self.node_info = NodeInfo("node1", "162.243.41.99", 8080)
            self.node_info = NodeInfo("node1", "localhost", 8080)
        
        # Send transaction if this succeeds
        # if self.txs:
        #     for tx in self.txs:
        #         self.send_new_tx(tx)
        
    def send_new_tx(self, tx):
        print("Sending transaction: " + str(tx))
        resp_dict = NodeClient.send_request(None, self.node_info, 'POST', "new_tx", tx.to_dict(), timeout=20)
        status = resp_dict["status"]
        
        if status == "ok":
            print("Transaction successfully added")
        else:
            raise Exception("Transaction was rejected: " + str(status))
        
    def get_last_tx(self, owner):
        print("Getting last transaction for " + str(owner))
        resp_dict = NodeClient.send_request(None, self.node_info, 'GET', "latest_tx", { "owner": owner }, timeout=20)
        status = resp_dict["status"]
        
        if status == "ok":
            prev_tx = resp_dict["previous_hash"]
            print("Previous transaction for {0} was {1}".format(owner, prev_tx))
            return prev_tx
        else:
            raise Exception("No previous transaction for owner " + str(owner))
        
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
    tx1 = tx_object("localhost", "Owner1", 1, None, None, previous_hash=None)
    tx2 = tx_object("localhost", "Owner1", 2, None, None, previous_hash=tx1.current_hash)
    tx3 = tx_object("localhost", "Owner1", 3, None, None, previous_hash=tx2.current_hash)
    tx4 = tx_object("localhost", "Owner1", 4, None, None, previous_hash=tx3.current_hash)
    tx5 = tx_object("localhost", "Owner1", 5, None, None, previous_hash=tx4.current_hash)
    tx6 = tx_object("localhost", "Owner1", 6, None, None, previous_hash=tx5.current_hash)
    tx7 = tx_object("localhost", "Owner1", 7, None, None, previous_hash=tx6.current_hash)
    tx8 = tx_object("localhost", "Owner1", 8, None, None, previous_hash=tx7.current_hash)
    tx9 = tx_object("localhost", "Owner1", 9, None, None, previous_hash=tx8.current_hash)
    tx10 = tx_object("localhost", "Owner2", 10, None, None, previous_hash=None)
    tx11 = tx_object("localhost", "Owner2", 11, None, None, previous_hash=tx10.current_hash)
    tx12 = tx_object("localhost", "Owner2", 12, None, None, previous_hash=tx11.current_hash)
    tx13 = tx_object("localhost", "Owner2", 13, None, None, previous_hash=tx12.current_hash)
    tx14 = tx_object("localhost", "Owner2", 14, None, None, previous_hash=tx13.current_hash)
    tx15 = tx_object("localhost", "Owner2", 15, None, None, previous_hash=tx14.current_hash)
    tx16 = tx_object("localhost", "Owner2", 16, None, None, previous_hash=tx15.current_hash)
    tx17 = tx_object("localhost", "Owner2", 17, None, None, previous_hash=tx16.current_hash)
    tx18 = tx_object("localhost", "Owner1", 18, None, None, previous_hash=tx9.current_hash)
    tx19 = tx_object("localhost", "Owner1", 19, None, None, previous_hash=tx18.current_hash)
    txs = [tx1, tx2, tx3, tx4, tx5, tx6, tx7, tx8, tx9, tx10, tx11, tx12, tx13, tx14, tx15, tx16, tx17, tx18, tx19]
    node = TxOriginNode(cnds_info)
    
    for tx in txs:
        node.send_new_tx(tx)
        print("Last Transaction: " + node.get_last_tx("Owner1"))
        time.sleep(0.50)
        
    print("Done")
        
    # except Exception as exc:
    #   print("Fatal Error: " + str(exc))

if __name__ == "__main__":
    main(sys.argv)