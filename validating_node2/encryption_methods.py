import requests
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES
import base64
import json
import pickle
import uuid
import sys

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]



class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))
    
    
class crypto_methods():
    def read_node_pubkey(self, filename): #filename ending with .pem
        node_public_key_file = open(filename, 'r')
        node_public_key_raw = node_public_key_file.read()
        node_public_key = RSA.importKey(node_public_key_raw)
        node_public_key_file.close()
        return node_public_key #returns the key object
    
    @staticmethod
    def check_cnds_key(self):
        cnds_public_key_text = r.json()["public-key"]
        cnds_provided_hash = r.json()["public-key-hash"]
        print "Generated Hash of the key should match with provided hash"
        computed_hash = SHA256.new(cnds_public_key_text).hexdigest()
        if computed_hash == cnds_provided_hash:
            print 'CNDS public key integrity verified'
            return True
        else:
            return False
        
    def cnds_pubencrypt(self,message): #to be called only after above check complete
        cnds_public_key_text = r.json()["public-key"]
        public_key = RSA.importKey(cnds_public_key_text)
        print "Sending CNDS a message"
        data_for_sending = {}
        #message = "Can you see this CNDS? I am testing my encryption chops :)"
        encrypted_message = public_key.encrypt(message, 32)[0]
        encrypted_message = pickle.dumps(encrypted_message)
        data_for_sending["message"] = encrypted_message
        data_for_sending["message-hash"] = SHA256.new(message).hexdigest()
        data=json.dumps(data_for_sending)
        return data
    
    
    def cnds_sessionkey_ex(self,session_key): #session_key = str(uuid.uuid1())[:32] 
        print "I can communicate in an encrypted fashion with the CNDS"
        print "I am going to exchange a session key with the CNDS"
        print "This will reduce computation on both side"
        
        result=cnds_pubencrypt(session_key)
        r = requests.post("http://localhost:8080/session_key_delivery", data=json.dumps(data_for_sending)) #can be put in calling function and localhost be changed
        success = r.json()["success"]
        return success #True or False
    
    def encrypted_joinreq(self,session_key,node_name,join_level="validating"):
        data_for_sending = {}
        print sys.getsizeof(session_key)
        node_public_key_raw = node_public_key_file.read()
        data_for_sending["node_name"] = node_name
        data_for_sending["public_key"] = node_public_key_raw
        data_for_sending["join_level"] = join_level
        message = json.dumps(data_for_sending)
        aes = AESCipher(session_key)
        encrypted_message = aes.encrypt(message)
        print encrypted_message
        final_message = {}
        final_message["message"] = encrypted_message
        final_message["message-hash"] = SHA256.new(message).hexdigest()
        print ('%s Sending node info to CNDS'% str(node_name)) 
        r = requests.post("http://localhost:8080/join_network", data=json.dumps(final_message))
        print r
        print 'Network join successfull'    
    
    #To get network info:
    #r = requests.get("http://localhost:8080/current_node_list")
    
    def decrypt(self,other_nodes_data): #encrypted data is the response received from get request, assumed to be in json
        other_nodes_data = r.json()
        encrypted_message = other_nodes_data["snapshot"]
        decrypted_message = aes.decrypt(encrypted_message)
        network_data = json.loads(decrypted_message)
        for node_name, node_details in network_data.iteritems():
            print node_name # This gives you the node name
            print json.loads(node_details) # This gives you all the node details
            #store the retreived data locally in a file 'network_info.json'
        
        return network_data #returning a dict
    
        
    def gen_decrypt(self,encrypted_message): #encrypted data has been converted from json
        #other_nodes_data = r.json()
        #encrypted_message = other_nodes_data["snapshot"]
        decrypted_message = aes.decrypt(encrypted_message)
        decrypted_json = json.loads(decrypted_message)
        return decrypted_json
    
    def sign_data(self,data): #data should be in json format, or can be dict. If dict, add conversion here
        with open('node1_config.json','r') as outfile:
            dict_state=json.load(outfile)
        expvtkey=dict_state['pvtkey']
        expvtkey[1]=long(expvtkey[1]) #convert the middle number to long
        cpvtkey=RSA.construct(expvtkey)
        
        hash1=SHA256.new(data).digest()
        
        signature=cpvtkey.sign(hash1,'')
        
        return signature #this is a tuple
    
    def verify_sign(self,data,signature):
        with open('node1_config.json','r') as outfile:
            dict_state=json.load(outfile)
        expubkey=dict_state['pubkey']
        expubkey[1]=long(expvtkey[1]) #convert the latter number to long
        cpubkey=RSA.construct(expubkey)
        
        hash1=SHA256.new(data).digest()
        
        result=cpubkey.verify(hash2,signature)
        print '****** Digital signature of owner verified *****'
        return result #this is a boolean
    
    

