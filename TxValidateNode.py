import sys
from twisted.web import server, resource
from twisted.internet import reactor, endpoints
from twisted.internet.endpoints import TCP4ServerEndpoint
from TxNodeUtil import *
from tx_format import *
import json
#from  import *
from blk_format import *
from hashcash import *

class TxValidateNode(resource.Resource):
    isLeaf = True

    def __init__(self, cnds_ip, local_port, local_ip):
        resource.Resource.__init__(self)
        self.reactor = reactor
        self.local_port = local_port
        self.local_ip = local_ip
        backlog = 10
        endpoint = TCP4ServerEndpoint(reactor, self.local_port, backlog, self.local_ip)
        endpoint.listen(server.Site(self))
        print("Node listening for connections on " + addr_port_to_str(self.local_ip, self.local_port))
        
    def run(self):
        self.reactor.run()
    
    def handle_get(self, uri, payload_dict, hash):
        print("GET " + uri + "\nPayload: " + str(payload_dict) + "\nHash: " + str(hash))
        if uri == "block":
            resp_dict = self.handle_block_lookup(payload_dict)
            
        return resp_dict
        
    def handle_post(self, uri, payload_dict, hash):
        print("POST " + uri + "\nPayload: " + str(payload_dict) + "\nHash: " + str(hash))
        if uri == "transaction":
            resp_dict = self.handle_add_tx(payload_dict)
        elif uri == "block":
            resp_dict = self.handle_add_block(payload_dict)
        
    def render_response(self, request, handler):
        request.setHeader(b"content-type", b"text/plain")
        
        uri = request.uri[2:]
        
        # TODO: set the ciphers based on which node issued the request
        request_cipher = None   
        response_cipher = None
       
        resp = None
        payload = None
        hash = None
        
        if "payload" in request.args:
            payload = request.args["payload"]
        if "hash" in request.args:    
            hash = request.args["hash"]
            
        if payload and hash:
            payload_dict = None
            
            try:
                payload_dict = deserialize_payload(payload, hash, request_cipher)
            except:
                print("Failed to deserialize request:")
                print("URI: " + str(uri))
                print("Request Payload: " + str(payload))
                print("Request Hash: " + str(hash))
            
            # The call to the handler should stay outside to allow crash if handler has error
            if payload_dict:
                resp_dict = handler(uri, payload_dict, hash)
                
                try:
                    resp = serialize_payload(resp_dict, response_cipher)
                except:
                    print("Failed to serialize response:")
                    print("URI: " + str(uri))
                    print("Request Payload: " + str(payload_dict))
                    print("Request Hash: " + str(hash))
                    print("Response Payload: " + str(resp_dict))
            
        if resp:
            return resp
        else:
            request.setResponseCode(404)
            return "Unknown request"
    
    def render_GET(self, request):
        return self.render_response(request, self.handle_get)
        
    def render_POST(self, request):
        return self.render_response(request, self.handle_post)

    
    
    
    
    
    #-----------------------------------------------------------------------------------VISHNU
    #Storing node info locally
    def store_network_info(self,network_info): #store response to nodeinfo request
        with open('network.json', 'w') as outfile:
            json.dump(network_info, outfile, indent=4, sort_keys=True)
    
    
    #Starting Blokchain Procedures
    #receive transactions from the originating node and store them till they overflow 
    def receive_new_tx(self, transaction): #transaction ={prev tx hash+asset data+current tx hash}
        # tx object ===> (self, origin, owner,value, owner_pubkey,upper_limit, previous_hash=None, current_hash=None):
        
        new_tx=tx_object(transaction['origin'], transaction['owner'],transaction['value'], transaction['owner_pubkey'],transaction['upper_limit'], transaction['previous_hash'], transaction['current_hash'])
        new_tx.to_string()
        
        with open('tx_database.json','r') as data_file:    
            dict_state = json.load(data_file)
        #dict_state[transaction['current_hash']]= {'previous_hash':transaction['previous_hash'],'current_dict':new_tx.to_dict()}
        
        dict_state[transaction['current_hash']]= new_tx.to_dict()  #Here the previous hash inside new_tx could be None or some dict, if None, it is a new origin node that is sending a tx
        
        with open('tx_database.json', 'w') as outfile:
            json.dump(dict_state, outfile, indent=4, sort_keys=True) #adding to unconfirmed pool
        
    
    def receive_tx_broadcast(self,transaction,new_node_info):#receive transaction broadcast and node information from a node contacting other for the first time
        new_tx=tx_object(transaction['origin'], transaction['owner'],transaction['value'], transaction['owner_pubkey'],transaction['upper_limit'], transaction['previous_hash'], transaction['current_hash'])
        new_tx.to_string()
        
        with open('tx_database.json','r') as data_file:    
            dict_state = json.load(data_file)
        #dict_state[transaction['current_hash']]= {'previous_hash':transaction['previous_hash'],'current_dict':new_tx.to_dict()}
        
        dict_state[transaction['current_hash']]= new_tx.to_dict()  #Here the previous hash inside new_tx could be None or some dict, if None, it is a new origin node that is sending a tx
        
        with open('tx_database.json', 'w') as outfile:
            json.dump(dict_state, outfile, indent=4, sort_keys=True) #adding to unconfirmed pool
        
        
        with open('network.json','r') as data_file:    
            dict_state = json.load(data_file)
       
        dict_state[new_node_info['nodename']]={'nodeip':new_node_info['nodeip'],'nodepubkey':new_node_info['nodepubkey']}   
        
        with open('network.json', 'w') as outfile:
            json.dump(dict_state, outfile, indent=4, sort_keys=True)#store the information about the new node
            
    
    def check_overflow(self): #returns True if overflow, otherwise returns false
        with open('tx_database.json','r') as data_file:    
            dict_state = json.load(data_file)
        
       
        if len(dict_state.keys()) >= 8:
            print '########## Transaction buffer full ###########'    
            # block=self.generate_block(dict_state)
            # block.toString()
            # with open('tx_database.json','w') as outfile:    
            #     json.dump('', outfile, indent=4, sort_keys=True) #clearing unconfirmed pool 
            # return block #this is an object, not a dict. Should we convert ?
            return dict_state
        else:
            return False
        
    def generate_block(self,dict_state): #dict_state is a dict of transactions
        print '########## Generating Block ###########'   
        
        with open('block_config.json','r') as data_file:    
            block_config = json.load(data_file)
        # with open('tx_database.json','r') as data_file:    
        #     dict_state = json.load(data_file)
        with open('newest_blkhash.json','r') as data_file: #reads the hash of the latest added block
            newest_hash_dict=json.load(data_file)
        prev_hash=newest_hash_dict['newest_hash']
        
        if prev_hash=='':
            prev_hash=None #check for error here
        
        block=block_object(block_config,dict_state,prev_hash)
        block.toString()
        return block #returns block with all info except nonce
    
    
    
    def hashcash_start(self,block): #gets the output of generate_block as input
        with open('tx_database.json','w') as outfile:    
            json.dump('', outfile, indent=4, sort_keys=True) #clearing unconfirmed pool 
        

        block_dict=block.to_dict()
        prev_hash=block_dict['block_header']['previoushash']
        header_hash=block_dict['magicnum'] +block_dict['block_header']['version']+ block_dict['block_header']['merklehash']+block_dict['block_header']['time']+block_dict['txcount']
        # difficulty=int(blockchain_state['prev_hash']['header']['difficulty']) #either add 1 to the latest difficulty value, or accept some global value)
        difficulty=12
        
        nonce_return=HashCash.generate(prev_hash,header_hash,difficulty) #might get stopped in the middle
        
        
        
        #Maybe move this ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
        block_dict['block_header']['nonce']=nonce_return
        
        with open('blockchain_database.json','r') as data_file:    
            blockchain_state = json.load(data_file) #returns the entire blockchain        
        
        #should we include previous hash here ? Will that work with the nonce while verification ? because its only used for comparison in the generation of nonce
        hashdata=block_dict['magicnum'] +block_dict['block_header']['version']+ block_dict['block_header']['merklehash']+block_dict['block_header']['time']+block_dict['txcount']+str( block_dict['block_header']['nonce'])
        block_hash=SHA512.new(bytes(hashdata)).digest()
        
        
        blockchain_state[block_hash]=block_dict
        
        with open('blockchain_database.json','w') as outputfile:    
            json.dump(blockchain_state,outputfile,indent=4, sort_keys=True) #writes newly generated block to block chain  
        
        with open('newest_blkhash.json','w') as data_file: #stores the hash of the latest added block
            json.dump({'newest_hash':block_hash},data_file,indent=4, sort_keys=True)
            
        
        #send block to broadcast
        block_broadcast={'block_hash':block_hash,'block_dict':block_dict}
            
            

    def validate_block(self, block_broadcast): # Done on receiving a block from another node (not on getting every new tx). This might take long. 

        with open('blockchain_database.json','r') as data_file:    
            blockchain_dict = json.load(data_file,object_pairs_hook=OrderedDict ) #returns the entire blockchain, with the ordered dict

        tx_order_dict=blockchain_dict['transactions']
        flag=False
        root_verify= self.set_merkle(tx_order_dict)
        if root_verify==str(block_broadcast['block_dict']['block_header']['merklehash']):
            print('========================= Merkle root for block %s is Valid !==============================' % (block_broadcast['block_hash']))
            flag=True
        else:
            print('========================= Merkle root for block %s is NOT Valid !==============================' % (block_broadcast['block_hash']))
            return False
            
        
        
        if(flag==True):
            with open('newest_blkhash.json','r') as data_file: #reads the hash of the latest added block
                    newest_hash_dict=json.load(data_file)
            newest_blkhash=newest_hash_dict['newest_hash']
            #check hash of latest block
            if block_broadcast['block_dict']['block_header']['previoushash']==newest_blkhash:
                tx_verify=''
                for tx in tx_order_dict.keys():
                    blockhash=newest_blkhash
                    while blockhash != None:
                        #value = d.get(key, "empty")
                        tx_verify=blockchain_dict[blockhash]['transactions'].get(tx['previous_hash'])
                        if tx_verify not in ('', None):
                            print ('------------------ Transaction Verified !! ----------------------')
                            break
                        else:
                            blockhash=blockchain_dict[blockhash]['block_header']['previoushash']
                
                    
                    
                    if tx_verify in ('',None):
                        print ('------------------ A transaction is not verified !! ----------------------')
                        return False
                
                
                #If all transactions valid, store block . Reuse above code to add to file
        
                with open('blockchain_database.json','r') as data_file:    
                    blockchain_state = json.load(data_file) #returns the entire blockchain
                
                
                blockchain_state[block_broadcast['block_hash']]=block_broadcast['block_dict']
                
                with open('blockchain_database.json','w') as outputfile:    
                    json.dump(blockchain_state,outputfile,indent=4, sort_keys=True) #writes newly generated block to block chain  
                
                with open('newest_blkhash.json','w') as data_file: #stores the hash of the latest added block
                    json.dump({'newest_hash':block_hash},data_file,indent=4, sort_keys=True)
            
                
                
            else:
                print('Previous block not in blockchain !! ')
            
            
            
            
            
    
    def set_merkle(self,tx_order_dict):
        #tx_order_dict= OrderedDict(tx_dict)
        hashes1=[]
        hashes2=[]
        hashes3=[]
        
        i=0
        while (i< len(tx_order_dict.keys())):#every key is a hash of the tx, range=8
            temp=tx_order_dict.keys()[i]+tx_order_dict.keys()[i+1]
            i=i+2
            hashes1.append(SHA512.new(bytes(temp)).digest()) #has 4 hashes
        i=0
        while (i< len(hashes1)):#every key is a hash of the tx, range=4
            temp=hashes1[i]+hashes1[i+1]
            i=i+2
            hashes2.append(SHA512.new(bytes(temp)).digest()) #has 2 hashes
        i=0
        while (i< len(hashes2)):#every key is a hash of the tx, range=2
            temp=hashes2[i]+hashes2[i+1]
            i=i+2
            root_hash=SHA512.new(bytes(temp)).digest() #has the root hash
            print ('Merkle root calculated :')
            print root_hash
            
        return root_hash
        

    def merge_unconfirmedpool(self,pool1,pool2,pool3):
        with open('tx_database.json','r') as data_file:    
            pool_state = json.load(data_file)
        
        
        pool1_keys=pool1.keys()
        pool2_keys=pool2.keys()
        pool3_keys=pool3.keys()
        
        common=((pool1_keys | pool2_keys) & pool3_keys)
        common=list(common)
        final=pool1.copy()
        final.update(pool2) #does the union
        # del c['b']
        for i in common:
            del final[i] #delete the common elements
            
        return final


def main(args):
    cnds_ip = "localhost"
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
    node = TxValidateNode(cnds_ip, local_port, local_ip)
    node.run()

if __name__ == "__main__":
    main(sys.argv)