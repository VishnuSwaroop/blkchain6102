import sys
from NodeServer import *
from NodeClient import *
from ProofOfWork import *

class TxValidateNode(NodeServer):    
    def __init__(self, cnds_info, node_config):
        self.reactor = reactor
        self.uc_pool = []
        self.proof_of_work = None
        self.network_info = None
        
        self.local_info = node_config
        self.cnds_info = cnds_info
        
        self.request_join()
        
    def run(self):
        self.reactor.run()
        
    def start_server(self):
        print("Starting transaction validation node server")
        NodeServer.__init__(self, self.local_info)
        print("Node listening for connections on {0}".format(self.local_info))
        
    def request_join(self):
        print("Requesting join")
        req_dict = { "join": True }
        NodeClient.create_request(self.local_info, self.cnds_info, "POST", "join", req_dict, self.handle_join_resp)
        
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
        NodeClient.create_request(self.local_info, self.cnds_info, "GET", "network", req_dict, self.handle_network_info_resp)
    
    def handle_network_info_resp(self, payload_dict, fail):
        print("Network info response received")
        if not fail:
            self.network_info = TxValidateNode.get_network_info_from_resp(payload_dict)
            
            if self.network_info:
                print("Network info retrieved: " + str(self.network_info))
                self.start_server()
            else:
                raise Exception("Failed to get network info. Invalid response from CNDS")
        else:
            raise Exception("Failed to get network info: " + str(fail))
        
    @staticmethod
    def get_network_info_from_resp(resp):
        network_info = { }
        for name, node_dict in resp.iteritems():
            network_info[name] = NodeInfo.from_dict(node_dict)
        return network_info
        
    def check_and_add_node_info(self, client_info):
        # TODO: was there something to do here?
        if not client_info.name in self.network_info:
            print("Discovered new node at {0}".format(client_info))
            self.network_info[client_info.name] = client_info
    
    def handle_get(self, fcn, payload_dict, client_info):
        print("Function [{0}] from {1} Payload: {2}".format(fcn, client_info, payload_dict))
        resp_dict = None
        if fcn == "blockchain":
            resp_dict = self.handle_get_blockchain(payload_dict)
            
        return resp_dict
        
    def handle_post(self, fcn, payload_dict, client_info):
        print("Function [{0}] from {1} Payload: {2}".format(fcn, client_info, str(payload_dict)))
        resp_dict = None
        
        if fcn == "add_tx":
            self.check_and_add_node_info(client_info)
            resp_dict = self.handle_add_tx(payload_dict)
        elif fcn == "new_tx":
            resp_dict = self.handle_new_tx(payload_dict)
        elif fcn == "block":
            resp_dict = self.handle_add_block(payload_dict, client_info)
            
        return resp_dict
    
    def handle_new_tx(self, tx):
        print("Received new transaction")
        resp_dict = self.handle_add_tx(tx)
        # TODO: could refuse to broadcast transaction until after it is validated?
        self.broadcast_message("POST", "add_tx", tx)
        return resp_dict
    
    def handle_add_tx(self, tx):
        print("Adding transaction")
        
        # TODO: validate transaction
        
        # Add to unconfirmed pool (uc)
        self.uc_pool.append(tx)
        print("UC Pool Size: {0}".format(len(self.uc_pool)))
        
        # dict_state = self.check_overflow()
        # if dict_state:
        #     self.generate_block(dict_state)
        # If uc overflows, begin working on proof of work
        max_size = 4
        if len(self.uc_pool) >= max_size:
            block = self.uc_pool[:max_size]     # only take up to the max size for the current block
            self.uc_pool = self.uc_pool[max_size:]
            try:
                self.start_proof_of_work(block)
            except:
                self.return_aborted_transactions(block)
            
        return { "status": "ok" }
    
    def handle_add_block(self, block, client_info):
        # TODO: validate block
        # TODO: validate transactions
        
        # TODO: Read blockchain from disk
        local_chain = None
        # TODO: Determine chain length
        local_chain_len = 0
        # TODO: Read most recent hash of local chain
        latest_hash = None
        
        if block.previoushash == latest_hash:
            # Abort current proof of work
            old_uc_pool = self.abort_proof_of_work()
            # TODO: add to blockchain
            # TODO: write blockchain back to disk    
        else:
            pass
            # TODO: query sender's chain for previous hash of the block recently received
            # remote_chain = self.request_blockchain(
            # TODO: check for longer chain and replace local chain if sender's is longer
        
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
        self.uc_pool.extend(old_uc_pool)    
    
    def broadcast_message(self, method, fcn, msg_dict):
        if self.network_info:
            print("Broadcasting message: {0} [{1}] {2}".format(method, fcn, str(msg_dict)))
            for node_name, node_info in self.network_info.iteritems():
                if not (node_info.ip == self.local_info.ip and node_info.port == self.local_info.port):
                    print("Broadcasting to {0}".format(node_info))
                    NodeClient.create_request(self.local_info, node_info, method, fcn, msg_dict, None)
        else:
            print("Failed to broadcast message because CNDS has yet to respond with network info")
    
    def handle_broadcast_resp(self, resp_dict, fail):
        # TODO: remove nodes that do not respond from the list after some number of failed attempts
        pass
    
    def handle_get_blockchain(self, payload_dict):
        start_hash = payload_dict["start_hash"]
        num_blocks = payload_dict["num_blocks"]
        
        if not start_hash:
            # TODO: read latest hash from disk
            start_hash = None
        
        # TODO: load in blockchain
        local_chain = None
        
        chain_segment = { }
        
        # Read segment of chain starting at start_hash and going back num_blocks
        if start_hash in local_chain:
            cur_hash = start_hash
            for i in xrange(0, num_blocks):
                if cur_hash in local_chain:
                    chain_segment[cur_hash] = local_chain[cur_hash]
                    cur_hash = chain_segment[cur_hash].previoushash
                else:
                    break
        return chain_segment
        
    def request_blocks(self, node_info, num_blocks, start_hash):
        print("Requesting blocks from {0}".format(node_info))
        req_dict = { "num_blocks": num_blocks, "start_hash": start_hash }
        NodeClient.create_request(self.local_info, node_info, "GET", "blocks", req_dict, resp_handler)
        
    def handle_blocks_response(self, payload_dict, sender_info):
        print("Blocks received from {0}".format(sender_info))
        pass
    
def main(args):
    node_config_file = None
    cnds_info_file = None
    
    cnds_info = NodeInfo("leader1", "localhost", 1234)
    node_config = NodeInfo("node1", "localhost", 1235)
        
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
        cnds_info = load_node_config(cnds_info_file)
    
    # print("Node Configuration: " + str(node_config))
    # print("CNDS Configuration: " + str(cnds_info))
    
    # Run server
    print("Starting Transaction Validation Node service")
    node = TxValidateNode(cnds_info, node_config)
    node.run()

if __name__ == "__main__":
    main(sys.argv)