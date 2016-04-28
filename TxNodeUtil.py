import json
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA512

def addr_port_to_str(ip, port):
    return ip + ":" + str(port)
    
def addr_to_str(addr):
    return addrPortToStr(addr.host, addr.port)
    
def encrypt_payload(payload_str, cipher):
    return payload_str
    #return cipher.encrypt(payload_str)
    #stride = 470        # TODO: how is this size related to key size? any larger and cipher.encrypt will complain
    #blocks = []
    #for i in xrange(0, len(payload_str)-1, stride):
    #    end_stride = min(i+stride-1, len(payload_str)-1)
    #    blocks.append(cipher.encrypt(payload_str[i:end_stride]))
    #return "".join(blocks)
    
def decrypt_payload(encrypted_payload_str, cipher):
    return encrypted_payload_str
    #return cipher.decrypt(encrypted_payload_str)
    #stride = 470        # TODO: how is this size related to key size? any larger and cipher.encrypt will complain
    #blocks = []
    #for i in xrange(0, len(encrypted_payload_str)-1, stride):
    #    end_stride = min(i+stride-1, len(encrypted_payload_str)-1)
    #    blocks.append(cipher.decrypt(encrypted_payload_str[i:end_stride]))
    #return "".join(blocks)
    
def serialize_payload(payload_dict, cipher):
    # Serialize message dictionary to JSON payload
    payload = json.dumps(payload_dict)
    
    # Encrypt JSON payload
    if cipher:
        payload = NodeMessage.encrypt_payload(payload, cipher)
        
    # Compute hash of encrypted payload
    datahash = SHA512.new(bytes(str(payload))).digest()
    
    # Create binary message string
    msg_str = "".join([payload, datahash])  # TODO: should really use something like bson for this...
        
    return msg_str
    
def deserialize_payload(msg_str, cipher):
    # Interpret HTTP binary message string
    end = len(msg_str)-64       # TODO: should really use something like bson for this...
    datahash = msg_str[end:]
    payload = msg_str[:end]
    
    # Compute hash of encrypted data
    computed_hash = SHA512.new(payload)
    
    # Verify hash
    if computed_hash.digest() != datahash:
        print("Payload deserialization failed due to invalid hash")
        return None
        
    # Decrypt message
    if cipher:
        payload = NodeMessage.decrypt_payload(payload, cipher)
    
    # Get payload dictionary
    payload_dict = json.loads(payload)

    # If json.load returns None, an empty dictionary was sent
    if not payload_dict:
        payload_dict = { }
        
    return payload_dict