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

from AESCipher import *
    
# cnds_url = "http://localhost:8080/"
cnds_url = "http://162.243.199.107:8080/"
# cnds_url = "http://128.61.79.90:8081/"
    
def read_node_pubkey(filename): #filename ending with .pem
    node_public_key_file = open(filename, 'r')
    node_public_key_raw = node_public_key_file.read()
    node_public_key = RSA.importKey(node_public_key_raw)
    node_public_key_file.close()
    return node_public_key, node_public_key_raw #returns the key object
    
def get_and_check_cnds_key():
    r = requests.get(cnds_url + "/public_key")
    cnds_public_key_text = r.json()["public-key"]
    cnds_provided_hash = r.json()["public-key-hash"]
    print "Generated Hash of the key should match with provided hash"
    computed_hash = SHA256.new(cnds_public_key_text).hexdigest()
    if computed_hash == cnds_provided_hash:
        print 'CNDS public key integrity verified'
        return cnds_public_key_text
    else:
        return False
        
def cnds_pubencrypt(message, cnds_public_key_text): #to be called only after above check complete
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


def cnds_sessionkey_ex(session_key, cnds_public_key_text): #session_key = str(uuid.uuid1())[:32] 
    print "I can communicate in an encrypted fashion with the CNDS"
    print "I am going to exchange a session key with the CNDS"
    print "This will reduce computation on both side"
    
    result=cnds_pubencrypt(session_key, cnds_public_key_text)
    r = requests.post(cnds_url + "/session_key_delivery", result) #can be put in calling function and localhost be changed
    success = r.json()["success"]
    return success #True or False

def encrypted_joinreq(session_key,node_name,pubkey_filename,join_level="validating"):
    data_for_sending = {}
    print sys.getsizeof(session_key)
    node_public_key, node_public_key_raw = read_node_pubkey(pubkey_filename)
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
    r = requests.post(cnds_url + "/join_network", data=json.dumps(final_message))
    #print 'Network join successfull'
    try:
        resp = r.json()
    except:
        resp = r.text
    
    return resp

#To get network info:
#r = requests.get("http://localhost:8080/current_node_list")

def get_network_info(session_key):
    r = requests.get(cnds_url + "/current_node_list")
    network_data = decrypt(session_key, r.json())
    return network_data

def get_validating_node():
    r = requests.get(cnds_url + "/get_validating_node")
    resp_dict = r.json()
    if resp_dict["status"] == "Available":
        return resp_dict["suggested_node"]
    else:
        return resp_dict["status"]

def decrypt(session_key, other_nodes_data): #encrypted data is the response received from get request, assumed to be in json
    encrypted_message = other_nodes_data["snapshot"]
    aes = AESCipher(session_key)
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
    
    

