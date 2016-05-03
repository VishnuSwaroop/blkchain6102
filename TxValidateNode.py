import sys
import json
from NodeServer import *
from NodeClient import *
from ProofOfWork import *
from tx_format import *
from blk_format import *
#from hashcash import *
from globalhash import *
from encryption_methods import *

class TxValidateNode(NodeServer):    
    default_port = 8080
    def __init__(self, cnds_info, node_config):
        self.reactor = reactor
        self.uc_pool = []
        self.proof_of_work = None
        self.network_info = { }
        
        self.local_info = node_config
        self.cnds_info = cnds_info
        
        pubkey_filename = "node_public_key.pem"
        
        real_cnds = True
        if real_cnds:
            self.connect_to_cnds(pubkey_filename)
        else:
            self.network_info = { "node1": NodeInfo("node1", "162.243.41.99", 8080), "node2": NodeInfo("node2", "128.61.124.49", 8080) }
            TxValidateNode.store_network_info(self.network_info)
            print("Network info retrieved: " + str(self.network_info))
            self.start_server()
        
    def run(self):
        self.reactor.run()
        
    def start_server(self):
        print("Starting transaction validation node server")
        NodeServer.__init__(self, self.local_info)
        print("Node listening for connections on {0}".format(self.local_info))
      
    def connect_to_cnds(self, pubkey_filename):
        # Get node public key from file
        self.node_public_key = read_node_pubkey(pubkey_filename)
        
        # Retrieve CNDS key
        cnds_public_key_text = get_and_check_cnds_key()
        
        # Generate session key
        self.node_session_key = str(uuid.uuid1())[:32]
        
        # Exchange session key
        if not cnds_sessionkey_ex(self.node_session_key, cnds_public_key_text):
            raise Exception("Failed exchanging session keys with CNDS")    
        
        # Join network
        join_status = encrypted_joinreq(self.node_session_key, self.local_info.name, pubkey_filename)
        
        if not join_status:
            raise Exception("Failed to join")
        
        net_info = get_network_info(self.node_session_key)
        
        self.network_info = TxValidateNode.get_network_info_from_resp(net_info)
        
        # Store network information to disk
        TxValidateNode.store_network_info(self.network_info)
        
        print("Network info retrieved: " + str(self.network_info))
        
        # Start http server for validating node
        self.start_server()
      
    """  
    def request_join(self):
        print("Requesting join")
        req_dict = { "join": True }
        payload_dict = NodeClient.send_request(self.local_info, self.cnds_info, "POST", "join", req_dict)
        if payload_dict["status"] == "approved":
            print("Successfully joined")
            self.request_network_info()
        else:
            print("CNDS rejected join")
        
    def request_network_info(self):
        print("Requesting network info")
        req_dict = { "get_nodes": True }
        payload_dict = NodeClient.send_request(self.local_info, self.cnds_info, "GET", "network", req_dict)
        self.network_info = TxValidateNode.get_network_info_from_resp(payload_dict)
            
        if self.network_info:
            print("Network info retrieved: " + str(self.network_info))
            TxValidateNode.store_network_info(self.network_info)
            self.start_server()
        else:
            raise Exception("Failed to get network info. Invalid response from CNDS")
    """
    @staticmethod
    def get_network_info_from_resp(resp):
        network_info = { }
        for node_name, node_details in resp.iteritems():
            node_dict = json.loads(node_details)
            network_info[node_name] = NodeInfo(node_name,
                                          node_dict["ip_address"],
                                          TxValidateNode.default_port,
                                          node_dict["public_key"])
        return network_info
    
    @staticmethod
    def get_network_info_from_dict(d):
        network_info = { }
        for node_name, node_dict in d.iteritems():
            network_info[node_name] = NodeInfo.from_dict(node_dict)
        return network_info
    
    @staticmethod
    def load_network_info():
        network_info = None
        with open('network.json','r') as data_file:    
            network_info = json.load(data_file)
        return TxValidateNode.get_network_info_from_dict(network_info)
    
    @staticmethod
    def store_network_info(network_info):
        with open('network.json', 'w') as outfile:
            json.dump(TxValidateNode.get_network_info_dict(network_info), outfile, indent=4, sort_keys=True)#store the information about the new node
    
    @staticmethod
    def get_network_info_dict(network_info):
        network_info_dict = { }
        for name, node in network_info.iteritems():
            network_info_dict[name] = node.get_dict()
        return network_info_dict
    
    @staticmethod
    def store_network_info(network_info): #store response to nodeinfo request
        with open('network.json', 'w') as outfile:
            json.dump(TxValidateNode.get_network_info_dict(network_info), outfile, indent=4, sort_keys=True)
        
    def check_and_add_node_info(self, client_info):
        if client_info.name not in self.network_info:
            print("Discovered new node at {0}".format(client_info))
            self.network_info = TxValidateNode.load_network_info()
            self.network_info[client_info.name] = client_info
            TxValidateNode.store_network_info(self.network_info)
    
    def handle_get(self, fcn, payload_dict, client_info):
        print("Function [{0}] from {1} Payload: {2}".format(fcn, client_info, payload_dict))
        resp_dict = None
        if fcn == "blockchain":
            resp_dict = self.handle_get_blockchain(payload_dict)
        elif fcn == "ping":
            print("Ping received from CNDS")
            resp_dict = { "status": "ok" }
        elif fcn == "latest_tx":
            resp_dict = self.handle_get_latest_tx(payload_dict)
            
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
    
    def handle_get_latest_tx(self, payload_dict):
        owner = payload_dict["owner"]
        tx_hashtable = load_global_hash()
        if owner in tx_hashtable:
            return { "previous_hash": tx_hashtable[owner] }
        return None
    
    def handle_new_tx(self, tx):
        print("Received new transaction")
        resp_dict = self.handle_add_tx(tx)
        # TODO: could refuse to broadcast transaction until after it is validated?
        self.broadcast_message("POST", "add_tx", tx)
        return resp_dict
    
    def handle_add_tx(self, transaction):
        print("Adding transaction")
        
        new_tx=tx_object(transaction['origin'], transaction['owner'],transaction['value'], transaction['owner_pubkey'],transaction['upper_limit'], transaction['previous_hash'], transaction['current_hash'])
        new_tx.to_string()
        
        
        #Global hash table check
        if global_hash_table(new_tx.to_dict()):
            with open('tx_database.json','r') as data_file:    
                uc_pool = json.load(data_file)
            #dict_state[transaction['current_hash']]= {'previous_hash':transaction['previous_hash'],'current_dict':new_tx.to_dict()}
            
            uc_pool[transaction['current_hash']]= new_tx.to_dict()  #Here the previous hash inside new_tx could be None or some dict, if None, it is a new origin node that is sending a tx
            
            with open('tx_database.json', 'w') as outfile:
                json.dump(uc_pool, outfile, indent=4, sort_keys=True) #adding to unconfirmed pool
                
            overflow_tx = self.check_overflow()
        else:
            return { "status": "previous transaction does not match records" }

        if overflow_tx and not self.proof_of_work:
            with open('tx_database.json','w') as outfile:    
                json.dump({}, outfile, indent=4, sort_keys=True) #clearing unconfirmed pool 
            self.start_proof_of_work(overflow_tx)
            
        return { "status": "ok" }
        
    def check_overflow(self): #returns True if overflow, otherwise returns false
        with open('tx_database.json','r') as data_file:    
            dict_state = json.load(data_file)
        
       
        if len(dict_state.keys()) >= 8:
            print '########## Transaction buffer full ###########'    
            return dict_state
        else:
            return False
    
    def set_merkle(self,tx_order_dict):
        #tx_order_dict= OrderedDict(tx_dict)
        hashes1=[]
        hashes2=[]
        hashes3=[]
        
        i=0
        while (i< len(tx_order_dict.keys())):#every key is a hash of the tx, range=8
            temp=tx_order_dict.keys()[i]+tx_order_dict.keys()[i+1]
            i=i+2
            hashes1.append(SHA512.new(bytes(temp)).hexdigest()) #has 4 hashes
        i=0
        while (i< len(hashes1)):#every key is a hash of the tx, range=4
            temp=hashes1[i]+hashes1[i+1]
            i=i+2
            hashes2.append(SHA512.new(bytes(temp)).hexdigest()) #has 2 hashes
        i=0
        while (i< len(hashes2)):#every key is a hash of the tx, range=2
            temp=hashes2[i]+hashes2[i+1]
            i=i+2
            root_hash=SHA512.new(bytes(temp)).hexdigest() #has the root hash
            print ('Merkle root calculated :')
            print root_hash
            
        return root_hash
    
    def validate_block(self, block_broadcast): # Done on receiving a block from another node (not on getting every new tx). This might take long. 
        
        difficulty = 12
        block_dict = block_broadcast['block_dict']
        previoushash = block_dict['block_header']['previoushash']
        #send same data as last time, but also pass the nonce
        header_data = str(block_dict['magicnum']) +str(block_dict['block_header']['version'])+str( block_dict['block_header']['merklehash'])+str(block_dict['block_header']['time'])+str(block_dict['txcount']) #+str( block_dict['block_header']['nonce'])
        
        if not ProofOfWork.verify(previoushash, header_data, block_dict['block_header']['nonce'], difficulty):
            return False
    
        tx_order_dict=block_broadcast['block_dict']['transactions']
        flag=False
        root_verify= self.set_merkle(tx_order_dict)
        if root_verify==str(block_broadcast['block_dict']['block_header']['merklehash']):
            print('========================= Merkle root for block %s is Valid !==============================' % (block_broadcast['block_hash']))
            flag=True
        else:
            print('========================= Merkle root for block %s is NOT Valid !==============================' % (block_broadcast['block_hash']))
            return False
            
        
        
        if(flag==True):
            # with open('newest_blkhash.json','r') as data_file: #reads the hash of the latest added block
            #         newest_hash_dict=json.load(data_file)
            # 
            # if newest_hash_dict.get('newest_hash'):
            #     newest_blkhash=newest_hash_dict['newest_hash']
            # else:
            #     newest_blkhash=None
            # #check hash of latest block
            # if block_broadcast['block_dict']['block_header']['previoushash'] in (newest_blkhash, None, '', 'None'):
            #     tx_verify=''
            #     for tx in tx_order_dict.keys():
            #         blockhash=newest_blkhash
            #         while blockhash != None:
            #             #value = d.get(key, "empty")
            #             tx_verify=blockchain_dict[blockhash]['transactions'].get(tx['previous_hash'])
            #             if tx_verify not in ('', None):
            #                 print ('------------------ Transaction Verified !! ----------------------')
            #                 break
            #             else:
            #                 blockhash=blockchain_dict[blockhash]['block_header']['previoushash']
            #     
            #         
            #         
            #         if tx_verify in ('',None):
            #             print ('------------------ A transaction is not verified !! ----------------------')
            #             return False
                
                
            #If all transactions valid, store block . Reuse above code to add to file
            #TODO: Send confirmation back to the other validating node about this acceptance
            with open('blockchain_database.json','r') as data_file:    
                blockchain_state = json.load(data_file) #returns the entire blockchain
            
            
            blockchain_state[block_broadcast['block_hash']]=block_broadcast['block_dict']
            
            with open('blockchain_database.json','w') as outputfile:    
                json.dump(blockchain_state,outputfile,indent=4, sort_keys=True) #writes newly verified block to block chain  
            
            with open('newest_blkhash.json','w') as data_file: #stores the hash of the latest added block
                json.dump({'newest_hash':block_broadcast['block_hash']},data_file,indent=4, sort_keys=True)
        
            return True
            
        else:
            print('Previous block not in blockchain !! Sending query to other nodes for longest chain')
                
    def merge_unconfirmedpool(self,pool1,pool2,pool3):
        with open('tx_database.json','r') as data_file:    
            pool_state = json.load(data_file)
        
        
        pool1_keys=set(pool1.keys())
        pool2_keys=set(pool2.keys())
        pool3_keys=set(pool3.keys())
        
        common=((pool1_keys | pool2_keys) & pool3_keys)
        common=list(common)
        final=pool1.copy()
        final.update(pool2) #does the union
        # del c['b']
        for i in common:
            del final[i] #delete the common elements
            
        return final
    
    def handle_add_block(self, block_dict, client_info):
        if self.validate_block(block_dict):
            # Abort current proof of work
            old_block = self.abort_proof_of_work()
            
            # Read current blockchain
            with open('tx_database.json','r') as data_file:
                pool_state = json.load(data_file)
            
            # Merge unconfirmed pools
            old_uc_pool = {}
            if old_block:
                old_uc_pool = old_block.to_dict()["transactions"]
            final_uc_pool = self.merge_unconfirmedpool(old_uc_pool, pool_state, block_dict["block_dict"]["transactions"])
            
            # Write current blockchain
            with open('tx_database.json','w') as data_file:
                json.dump(final_uc_pool, data_file)
                
            return { "status": "ok" }
        else:
            # Query sender's chain to determine if it's longer
            #self.request_blocks(client_info, 5, block_dict["block_hash"])
            print("Failed to validate block. Continuing work on new transactions")
        
        return { "status": "rejected" }
        
    def generate_block(self,dict_state): #dict_state is a dict of transactions
        print '########## Generating Block ###########'   
        
        with open('block_config.json','r') as data_file:    
            block_config = json.load(data_file)
        # with open('tx_database.json','r') as data_file:    
        #     dict_state = json.load(data_file)
        with open('newest_blkhash.json','r') as data_file: #reads the hash of the latest added block
            newest_hash_dict=json.load(data_file)
            
        if newest_hash_dict != {}:
            prev_hash=newest_hash_dict['newest_hash']
        else:
            prev_hash = None
        
        block=block_object(block_config,dict_state,prev_hash)
        block.toString()
        return block #returns block with all info except nonce
    
    def start_proof_of_work(self, overflow_tx):
        print("Scheduling proof of work")
        if not self.proof_of_work:
            block = self.generate_block(overflow_tx)
            self.proof_of_work = ProofOfWork(self.reactor, block, self.proof_of_work_completed, self.proof_of_work_failed)
        else:
            raise Exception("Attempted to start proof of work while another is already running")
        
    def abort_proof_of_work(self):
        if self.proof_of_work:
            print("Aborting proof of work")
            aborted_transactions = self.proof_of_work.abort()
            self.proof_of_work = None
            return aborted_transactions
    
    @staticmethod
    def verify_num_resps(num_resps, network_info):
        num_nodes = len(network_info)
        print("Num responses: {0}/{1}".format(num_resps, num_nodes))
        return num_resps / num_nodes > 0.48
    
    def proof_of_work_completed(self, block, nonce):
        block_dict = block.to_dict()
        block_dict['block_header']['nonce']=nonce
        
        #should we include previous hash here ? Will that work with the nonce while verification ? because its only used for comparison in the generation of nonce
        header_data=str(block_dict['magicnum']) +str(block_dict['block_header']['version'])+ str(block_dict['block_header']['merklehash'])+str(block_dict['block_header']['time'])+str(block_dict['txcount'])+str( block_dict['block_header']['nonce'])
        block_hash=SHA512.new(bytes(header_data)).hexdigest()
        
        #send block to broadcast
        block_broadcast={'block_hash':block_hash,'block_dict':block_dict}
        num_resps = self.broadcast_message("POST", "block", block_broadcast)
        num_resps += 1 # for this node
        
        # Check for responses from 51% of nodes
        if TxValidateNode.verify_num_resps(num_resps, self.network_info):
            # Add block to local blockchain
            with open('blockchain_database.json','r') as data_file:    
                blockchain_state = json.load(data_file) #returns the entire blockchain        
            
            blockchain_state[block_hash]=block_dict
            
            with open('blockchain_database.json','w') as outputfile:    
                json.dump(blockchain_state,outputfile,indent=4, sort_keys=True) #writes newly generated block to block chain  
            
            with open('newest_blkhash.json','w') as data_file: #stores the hash of the latest added block
                json.dump({'newest_hash':block_hash},data_file,indent=4, sort_keys=True)
        else:
            # Return transactions back into unconfirmed pool
            # Read current blockchain
            with open('tx_database.json','r') as data_file:
                pool_state = json.load(data_file)
            
            # Merge unconfirmed pools
            final_uc_pool = self.merge_unconfirmedpool(block_dict["transactions"], pool_state, {})
            
            # Write current blockchain
            with open('tx_database.json','w') as data_file:
                json.dump(final_uc_pool, data_file)
        
        self.proof_of_work = None
        
    def proof_of_work_failed(self, failure, old_uc_pool):
        raise Exception("Hashcash thread threw an exception: {0}".format(str(failure)))
    
    def broadcast_message(self, method, fcn, msg_dict):
        num_successes = 0
        if self.network_info:
            print("Broadcasting message: {0} [{1}] {2}".format(method, fcn, str(msg_dict)))
            print(str(self.network_info))
            remove_nodes = []
            for node_name, node_info in self.network_info.iteritems():
                print("{0}:{1}".format(node_name, node_info))
                if node_name != self.local_info.name:
                    print("Broadcasting to {0}".format(node_info))
                    try:
                        resp = NodeClient.send_request(self.local_info, node_info, method, fcn, msg_dict, timeout=3)
                        if resp["status"] == "ok":
                            num_successes += 1
                    except:
                        # Remove nodes that do not respond from the list after some number of failed attempts
                        if hasattr(self.network_info[node_name], "failed_broadcasts"):
                            self.network_info[node_name].failed_broadcasts += 1
                            
                            if self.network_info[node_name].failed_broadcasts > 3:
                                remove_nodes.append(node_name)
                        else:
                            self.network_info[node_name].failed_broadcasts = 0
            
            # Actually remove the nodes                
            for node_name in remove_nodes:
                del self.network_info[node_name]
        else:
            print("Failed to broadcast message because CNDS has yet to respond with network info")
            
        return num_successes
    
    @staticmethod
    def read_latest_hash():
        latest_hash = None
        with open("newest_blkhash.json",'r') as data_file:
            latest_hash = json.load(data_file)
        return latest_hash
    
    @staticmethod
    def read_blockchain():
        local_chain = None
        with open("blockchain_database.json",'r') as data_file:
            local_chain = json.load(data_file)
        return local_chain
    
    @staticmethod
    def write_blockchain(chain):
        with open("blockchain_database.json",'w') as data_file:
            json.dump(data_file, chain)
    
    def handle_get_blockchain(self, payload_dict):
        start_hash = payload_dict["start_hash"]
        num_blocks = payload_dict["num_blocks"]
        
        # Read latest hash from disk if not specified
        if not start_hash:
            start_hash = TxValidateNode.read_latest_hash()
        
        # Load in blockchain
        local_chain = TxValidateNode.read_blockchain()
        
        # Read entire blockchain if num_blocks not specified or <= 0
        if not num_blocks or num_blocks <= 0:
            num_blocks = len(local_chain)
        
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
        
        chain_segment["start_hash"] = start_hash
                
        return chain_segment
        
    def request_blocks(self, node_info, num_blocks, start_hash):
        print("Requesting blocks from {0}".format(node_info))
        req_dict = { "num_blocks": num_blocks, "start_hash": start_hash }
        NodeClient.create_request(self.local_info, node_info, "GET", "blocks", req_dict, resp_handler)
    
    @staticmethod    
    def find_chain_intersection(local_chain, recv_chain, start_hash):
        recv_chain_sublen = 0
        found = False
        cur_hash = start_hash
        while not found and cur_hash:
            if cur_hash in local_chain:
                return cur_hash, recv_chain_sublen
            else:
                cur_hash = recv_chain[cur_hash].previoushash
                recv_chain_sublen += 1
        return None
    
    @staticmethod
    def count_chain_sublen(chain, start_hash, end_hash):
        chain_sublen = 0
        cur_hash = start_hash
        while cur_hash != end_hash and cur_hash:
            cur_hash = chain[cur_hash].previoushash
            chain_sublen += 1
        return chain_sublen
    
    @staticmethod
    def merge_chains(base, base_start, new_segment, intersection_hash):
        cur_hash = base_start
        while cur_hash != intersection_hash and cur_hash:
            prev_hash = base[cur_hash].previoushash
            del base[cur_hash]
            cur_hash = prev_hash
            
        base.update(new_segment)
        
    def handle_blocks_response(self, payload_dict, sender_info):
        print("Blocks received from {0}".format(sender_info))
        local_start_hash = TxValidateNode.read_latest_hash()
        recv_chain = payload_dict
        local_chain = TxValidateNode.read_blockchain()
        
        # Find where received chain links into local chain
        start_hash = recv_chain["start_hash"]
        intersection_hash, recv_chain_sublen = TxValidateNode.find_chain_intersection(local_chain, recv_chain, start_hash)
        
        # If found
        if intersection_hash:
            # Determine size of local chain between head and deviation
            local_chain_sublen = TxValidateNode.count_chain_sublen(local_chain, local_start_hash, intersection_hash)
            
            # Check if received chain is longer than local chain and replace if necessary
            if local_chain_sublen < recv_chain_sublen:
                local_chain = TxValidateNode.merge_chains(local_chain, local_start_hash, recv_chain, intersection_hash)
                TxValidateNode.write_blockchain(local_chain)
                
        else:
            # Request the entire blockchain from the node and repeat this handler when it is received
            self.request_blocks(sender_info, 0, None)
    
def main(args):
    node_config_file = None
    cnds_info_file = None
    
    cnds_info = NodeInfo("leader1", "", 8081)
    node_config = NodeInfo("node1", "", 8080)
        
    # Parse command line arguments
    for arg in args[1:]:
        if not node_config_file:
            if arg.isdigit():
                node_config.port = int(arg)
            else:
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