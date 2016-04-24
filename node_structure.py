import json
import random
from Crypto.PublicKey import RSA
from Crypto import Random
import Crypto
from Crypto.Hash import SHA512
from TxValidateNode import *


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
        
    
    def createnode(self, nodeip, cndsip): #Call create node in main, then give inputs for Node's IPaddress an CNDS info file path
        #Node name
        i=random.randint(0,10) 
        i="n"+str(i)
        self.nodename=i
        
        #Node public and private keys
        random_generator = Random.new().read
        key1 = RSA.generate(4096, random_generator)
        self.nodepvtkey=(key1.publickey().n,key1.publickey().e,key1.d)
        self.nodepubkey=(key1.publickey().n,key1.publickey().e)
        
        #Node IP address
        #sys.argv= input('Enter the IP address: ')
        #self.nodeip=sys.argv
        self.nodeip = nodeip
        
        #CNDS public key
        # sys.argv= input('Enter the CNDS info file path: ')
        
        with open('CNDSpubkey.json','r') as data_file:    
            networkdata = json.load(data_file)
        
        self.CNDSpubkey=tuple(networkdata["CNDSpubkey"])
        
        #CNDS IP and CNDS dom name
        self.CNDSdomname=networkdata["CNDSdomname"]
        #self.CNDSip= networkdata["CNDSip"]
        self.CNDSip = cndsip
        
        #Convert to json and store on disk
        nodedict={"nodename":self.nodename,
                  "CNDSdomname": self.CNDSdomname,
                  "CNDSip": self.CNDSip,
                  "CNDSpubkey": self.CNDSpubkey,
                  "nodeip": self.nodeip,
                  "nodepubkey": self.nodepubkey,
                  "nodepvtkey": self.nodepvtkey}
        
        with open('nodeinfo.json', 'w') as outfile:
            json.dump(nodedict, indent=4,sort_keys=True)
        
        return self
    
    def join_req(self):
        mssg_type=1
        node_info={"type":mssg_type,"nodename":self.nodename,"nodeip":self.nodeip,"nodepubkey":self.nodepubkey}
        CNDSrouting=self.CNDSip
        
        
        node_info_json=json.dumps(node_info, indent=4,sort_keys=True)
        tempkey=RSA.construct(self.CNDSpubkey)
        node_info_encrypt=tempkey.encrypt(node_info_json,32)
        
        
        datahash=SHA512.new()
        datahash.update(bytes(str(node_info_encrypt)))
        
        sendlist=[CNDSrouting,node_info_encrypt,datahash] #Sending the CNDS' IP address, encrypted node information, hash of the encrypted node information
        sendlist_json=json.dumps(sendlist)
        #Might need to add another hash function here for whole message
        return sendlist_json
    
    
    def connection_status(self, CNDSresponse):
        if CNDSresponse==True:
            self.online==True
        
        
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
    
    
            