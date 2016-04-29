import sys
from NodeServer import *
from NodeClient import *
from ProofOfWork import *

class TxValidateNode(NodeServer):    
    def __init__(self, cnds_info, node_config):
        self.reactor = reactor
        self.uc_pool = []
        
        self.local_ip = node_config["nodeip"]
        self.local_port = node_config["nodeport"]
        self.cnds_ip = cnds_info["CNDSip"]
        self.cnds_port = cnds_info["CNDSport"]
        
        self.request_join()
        
    def run(self):
        self.reactor.run()
        
    def start_server(self):
        print("Starting transaction validation node server")
        NodeServer.__init__(self, self.local_ip, self.local_port)
        print("Node listening for connections on " + addr_port_to_str(local_ip, local_port))
        
    def request_join(self):
        print("Requesting join")
        req_dict = { "join": True }
        NodeClient.create_request(self.cnds_ip, self.cnds_port, "POST", "join", req_dict, self.handle_join_resp)
        
    def handle_join_resp(self, payload_dict, fail):
        if not fail:
            if payload_dict["status"] == "approved":
                print("Successfully joined")
                self.request_network_info()
            else:
                print("CNDS rejected join")
        else:
            raise Exception("Failed to get network info: " + str(fail))
        
    def request_network_info(self):
        print("Requesting network info")
        req_dict = { "get_nodes": True }
        NodeClient.create_request(self.cnds_ip, self.cnds_port, "GET", "network", req_dict, self.handle_network_info_resp)
    
    def handle_network_info_resp(self, payload_dict, fail):
        if not fail:
            self.network_info = payload_dict
            print("Network info retrieved: " + str(self.network_info))
            self.start_server()
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
        # Add to unconfirmed pool (uc)
        self.uc_pool.append(tx)
        
        # If uc overflows, begin working on proof of work
        if len(self.uc_pool) > 4:
            block = self.uc_pool
            self.uc_pool = []
            self.start_proof_of_work(block)
            
        return { "status": "ok" }
    
    def handle_add_block(self, block):
        # TODO: validate block
        
        # TODO: validate transactions
        
        # Abort current proof of work
        old_uc_pool = self.abort_proof_of_work()
        
        # TODO: add block to blockchain
        
        return { "status": "ok" }
    
    def start_proof_of_work(self, block):
        print("Scheduling proof of work")
        if not self.proof_of_work:
            self.proof_of_work = ProofOfWork(self.reactor, block, self.proof_of_work_completed, self.proof_of_work_failed)
        else:
            raise Exception("Attempted to start proof of work while another is already running")
        
    def abort_proof_of_work(self):
        if self.proof_of_work:
            print("Aborting proof of work")
            aborted_transactions = self.proof_of_work.abort()
            self.proof_of_work = None
            return aborted_transactions
    
    def proof_of_work_completed(self, block, nonce):
        # TODO: update nonce
        self.broadcast_message("POST", "block", block)
        # TODO: add block to local blockchain
        self.proof_of_work = None
        
    def proof_of_work_failed(self, failure, old_uc_pool):
        print("Proof of work failed: {0}".format(str(failure)))
        self.return_aborted_transactions(old_uc_pool)
        self.proof_of_work = None
        
    def return_aborted_transactions(self, old_uc_pool):
        print("Txs from aborted block returned to UC pool")
        self.uc_pool.append(old_uc_pool)    
    
    def broadcast_message(self, method, fcn, msg_dict):
        if self.network_info:
            print("Broadcasting message: {0} [{1}] {2}".format(method, fcn, str(msg_dict)))
            for node_name, node_info in self.network_info.iteritems():
                ip = node_info["node_ip"]
                port = node_info["node_port"]
                if not (ip == self.local_ip and port == self.local_port):
                    print("Broadcasting to " + addr_port_to_str(ip, port))
                    NodeClient.create_request(ip, port, method, fcn, msg_dict, None)
        else:
            print("Failed to broadcast message because CNDS has yet to respond with network info")
    
    def handle_broadcast_resp(self, resp_dict, fail):
        # TODO: remove nodes that do not respond from the list after some number of failed attempts
        pass
    
def main(args):
    node_config_file = None
    cnds_info_file = None
    
    cnds_info = {
        "CNDSdomname": "leader1",
        "CNDSip": "localhost",
        "CNDSport": 1234,
        "CNDSpubkey": None
    }
   
    node_config = {
        "nodeip": "localhost",
        "nodeport": 1235,
        "nodename": "node1",
        "nodepvtkey": None,
        "nodepubkey": None
    }
        
    # Parse command line arguments
    for arg in args[1:]:
        if not node_config_file:
            node_config_file = arg
        else:
            cnds_info_file = arg
    
    # Load node config if specified
    if node_config_file:
        node_config = load_node_config(node_config_file)
        
    if cnds_info_file:
        cnds_info = load_cnds_config(cnds_info_file)
    
    # print("Node Configuration: " + str(node_config))
    # print("CNDS Configuration: " + str(cnds_info))
    
    # Run server
    print("Starting Transaction Validation Node service")
    node = TxValidateNode(cnds_info, node_config)
    node.run()

if __name__ == "__main__":
    main(sys.argv)