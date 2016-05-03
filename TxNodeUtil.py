import json
import bson
import pickle
from collections import OrderedDict
from uuid import uuid4
from AESCipher import *

from NodeInfo import *

def addr_port_to_str(ip, port):
    return ip + ":" + str(port)
    
def addr_to_str(addr):
    return addrPortToStr(addr.host, addr.port)
 
def serialize_payload(payload_dict, sender_info, cipher):
    # Serialize message dictionary to JSON payload
    payload = json.dumps(payload_dict)
    # payload = bson.BSON.encode(payload_dict)
    # payload = encode(payload_dict)
    
    # Encrypt JSON payload
    if cipher:
        encrypted_payload = cipher.encrypt(payload)
        encrypted_payload = pickle.dumps(encrypted_payload)
        #payload = NodeMessage.encrypt_payload(payload, cipher)
    else:
        encrypted_payload = payload
        
    # Compute hash of encrypted payload
    msg_hash = SHA256.new(payload).hexdigest()
    
    # Create binary message string
    #msg_str = "".join([payload, datahash])
    msg = {
        "message": encrypted_payload,
        "message-hash": msg_hash,
    }
    
    if sender_info:
        msg["sender_ip"] = sender_info.ip,
        msg["sender_port"] = sender_info.port
        msg["sender_name"] = sender_info.name
        
    return json.dumps(msg)

def decode_bson(payload_str):
    return bson.BSON(payload_str).decode()
    
def deserialize_payload(msg_dict, cipher):
    # Interpret HTTP binary message string
    #end = len(msg_str) - 128       # TODO: should really use something like bson for this...
    #datahash = msg_str[end:]
    #payload = msg_str[:end]
    
    #print("msg_str={0}\ndatahash={1}\npayload={2}".format(msg_str, datahash, payload))

    print("Message: {0}".format(msg_dict))
    
    if "sender_name" in msg_dict:
        sender_name = msg_dict["sender_name"]
    else:
        sender_name = None
        
    if "sender_ip" in msg_dict:
        sender_ip = msg_dict["sender_ip"]
    else:
        sender_ip = None
        
    if "sender_port" in msg_dict:
        sender_port = msg_dict["sender_port"]
    else:
        sender_port = None
        
    sender_info = NodeInfo(sender_name, sender_ip, sender_port)
    
    print("Sender Info: {0}".format(sender_info))
    
    encrypted_payload = msg_dict["message"]
    msg_hash = msg_dict["message-hash"]
    
    if cipher:
        encrypted_payload = pickle.loads(encrypted_payload)
        payload = cipher.decrypt(encrypted_payload)
    else:
        payload = encrypted_payload
    
    # Compute hash of unencrypted data
    computed_hash = SHA256.new(payload)
    
    # Verify hash
    if computed_hash.hexdigest() != msg_hash:
        print("Payload deserialization failed due to invalid hash")
        return None
    
    # Get payload dictionary
    payload_dict = json.loads(payload, object_pairs_hook=OrderedDict)
    # payload_dict = bson.BSON.decode(payload)
    # payload_dict = decode(payload)

    # If json.load returns None, an empty dictionary was sent
    if not payload_dict:
        payload_dict = { }
        
    return payload_dict, sender_info

def generate_node_config(node_config_path, nodeip, nodeport):
    nodename = str(uuid4())
    # TODO: this routine should validate nodeip/nodeport
    #Node public and private keys
    random_generator = Random.new().read
    key1 = RSA.generate(4096, random_generator)
    nodepvtkey=(long(key1.publickey().n),long(key1.publickey().e),long(key1.d))
    nodepubkey=(long(key1.publickey().n),long(key1.publickey().e))
    
    #Convert to json and store on disk
    node_config = {"name":nodename,
        "ip": nodeip,
        "port": nodeport,
        "pubkey": nodepubkey,
        "pvtkey": nodepvtkey}
    
    with open(node_config_path, 'w') as outfile:
        json.dump(node_config, outfile, indent=4, sort_keys=True)

def load_node_config(node_config_path):
    print("path: {0}".format(node_config_path))
    # Load from node info
    with open(node_config_path,'r') as data_file:
        node_config = json.load(data_file)
    # TODO: data validation on file inputs
    return NodeInfo.from_dict(node_config)

# def create_cnds_info_file(cnds_info_path, name, ip, port, pubkey):    
#     #Convert to json and store on disk
#     cnds_info = {"CNDSdomname":name,
#         "CNDSip": ip,
#         "CNDSport": port,
#         "CNDSpubkey": pubkey}
#     
#     with open(cnds_info_path, 'w') as outfile:
#         json.dump(cnds_info, outfile, indent=4, sort_keys=True)
# 
# def load_cnds_config(cnds_config_path):
#     # Load from CNDS info
#     with open(cnds_config_path,'r') as data_file:    
#         cnds_config = json.load(data_file)
#     
#     # TODO: validation on file input
#     # pubkey=networkdata["CNDSpubkey"]
#     # domname=networkdata["CNDSdomname"]
#     # ip=networkdata["CNDSip"]
#     # port=networkdata["CNDSport"]
#     # 
#     # return ip, port, pubkey, domname
#     return cnds_config
    
def create_cipher(key):
    if len(key) == 3:
        tup_key = (long(key[0]), long(key[1]), long(key[2]))
    elif len(key) == 2:
        tup_key = (long(key[0]), long(key[1]))
    else:
        raise Exception("key should be a list with 2 or 3 elements")
        
    return PKCS1_OAEP.new(RSA.construct(tup_key))

    