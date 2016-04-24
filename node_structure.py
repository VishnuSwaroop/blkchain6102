import json
import random
from Crypto.PublicKey import RSA
from Crypto import Random
import Crypto
from Crypto.Hash import SHA512
from NodeMessage import *

class node_methods:
    def __init__(self,nodename='',CNDSdomname='',CNDSip='',CNDSpubkey=(),nodeip='',nodepubkey=(),nodepvtkey=(),online=False):
        self.nodename=nodename
        self.CNDSdomname=CNDSdomname
        self.CNDSip= CNDSip
        self.CNDSpubkey= CNDSpubkey
        self.nodeip=nodeip
        self.nodepubkey=nodepubkey 
        self.nodepvtkey=nodepvtkey
        self.online=online
    
    def createnode(self, nodeip, cnds_info_path): #Call create node in main, then give inputs for Node's IPaddress an CNDS info file path
        #Node name
        i=random.randint(0,10) 
        i="n"+str(i)
        self.nodename=i
        
        #Node public and private keys
        print("Creating public and private keys")
        random_generator = Random.new().read
        key1 = RSA.generate(4096, random_generator)
        self.nodepvtkey=(long(key1.publickey().n),long(key1.publickey().e),long(key1.d))
        self.nodepubkey=(long(key1.publickey().n),long(key1.publickey().e))
        
        #Node IP address
        self.nodeip = nodeip
        
        #CNDS public key
        print("Loading CNDS information")
        with open(cnds_info_path,'r') as data_file:    
            networkdata = json.load(data_file)
        
        cndspubkey = networkdata["CNDSpubkey"]
        self.CNDSpubkey=(long(cndspubkey[0]), long(cndspubkey[1]))
        
        #CNDS IP and CNDS dom name
        self.CNDSdomname=networkdata["CNDSdomname"]
        self.CNDSip=networkdata["CNDSip"]
        
        #Convert to json and store on disk
        nodedict={"nodename":self.nodename,
                  "CNDSdomname": self.CNDSdomname,
                  "CNDSip": self.CNDSip,
                  "CNDSpubkey": self.CNDSpubkey,
                  "nodeip": self.nodeip,
                  "nodepubkey": self.nodepubkey,
                  "nodepvtkey": self.nodepvtkey}
        
        print("Saving node info")
        with open('nodeinfo.json', 'w') as outfile:
            json.dump(nodedict, outfile, indent=4, sort_keys=True)
            
        # Create ciphers
        print("Creating ciphers")
        self.CNDScipher = PKCS1_OAEP.new(RSA.construct(self.CNDSpubkey))
        self.nodecipher = PKCS1_OAEP.new(RSA.construct(self.nodepvtkey))
    
    def join_req(self):
        print("Sending join request")
        node_info={"nodename":self.nodename,"nodeip":self.nodeip,"nodepubkey":self.nodepubkey}
        return NodeMessage(NodeMessages.JoinRequest, node_info, self.CNDScipher)
    
    def handle_join_resp(self, CNDSresponse):
        print("Receiving join response")
        if CNDSresponse["approved"]==True:
            print("Node joined successfully")
            self.online==True
    
    def handle_ping_req(self, CNDSreq):
        print("Sending ping response")
        tag = 0
        if CNDSreq["tag"]:
            tag = CNDSreq["tag"]
        return NodeMessage(NodeMessages.PingResponse, {"tag": tag}, self.nodecipher)
        
    def node_info_req(self):
        info_needed=True
        sendlist=[self.CNDSip,info_needed] #is digital signature required here  ?? Do all messages from everyone need a digital signature ?
    
    def save_node_info(self,network_info): #network_info should be [encrypted message, hash of encrypted message, digital signature]
        tempkey=RSA.construct(self.CNDSpubkey)
        calc_hash = SHA512.new(network_info[0])
        hash_verify=(calc_hash.hexdigest()==network_info[1].hexdigest())
        
        
        #might need to add another HASH test here !! To verify the entire message
        if (hash_verify == True):
            dec_data=tempkey.decrypt(network_info[0])
        else:
            print('Hash function failed, hence cannot save node information')
        
        
        origin_verify=tempkey.verify(calc_hash.digest(),network_info[2])
        
        if(origin_verify==True):
            if(hash_verify==True):
                network_info_dict=json.loads(dec_data)
                with open('NetworkInfo.json', 'w') as outfile:
                    json.dump(network_info_dict, outfile, indent=4, sort_keys=True) #Storing the received data locally, so that we can use it if the system restarts
        else:
            print('Origin test failed because signatures do not match')
            
    def iamalive(self):
        return self.online
    
    
            