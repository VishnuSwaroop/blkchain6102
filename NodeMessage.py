import json
from enum import Enum
from struct import *
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA512

class NodeMessages(Enum):
    Null = 0
    JoinRequest = 1
    JoinResponse = 2
    PingRequest = 3
    PingResponse = 4
    NodeInfoRequest = 5
    NodeInfoResponse = 6
    
# Messages are serialized in the following format:
# Field Name            Size (bytes)
# Message Type          2
# Payload               Variable
# Payload Hash          64
	
class NodeMessage:
    def __init__(self, msg_type, payload_dict, cipher):
        self.msg_type = msg_type
        self.cipher = cipher
        self.payload_dict = payload_dict
    
    @staticmethod
    def encrypt_payload(payload_str, cipher):
        return payload_str
        #stride = 470        # TODO: how is this size related to key size? any larger and cipher.encrypt will complain
        #blocks = []
        #for i in xrange(0, len(payload_str)-1, stride):
        #    end_stride = min(i+stride-1, len(payload_str)-1)
        #    blocks.append(cipher.encrypt(payload_str[i:end_stride]))
        #return "".join(blocks)
        
    @staticmethod
    def decrypt_payload(encrypted_payload_str, cipher):
        return encrypted_payload_str
        #stride = 470        # TODO: how is this size related to key size? any larger and cipher.encrypt will complain
        #blocks = []
        #for i in xrange(0, len(encrypted_payload_str)-1, stride):
        #    end_stride = min(i+stride-1, len(encrypted_payload_str)-1)
        #    blocks.append(cipher.decrypt(encrypted_payload_str[i:end_stride]))
        #return "".join(blocks)
        
    def serialize(self):
        # Serialize message dictionary to JSON payload
        payload = json.dumps(self.payload_dict, indent=4, sort_keys=True)
        #print(payload)
        
        # Encrypt JSON payload
        if self.cipher:
            payload = NodeMessage.encrypt_payload(payload, self.cipher)
        
        # Compute hash of encrypted payload
        datahash = SHA512.new(bytes(str(payload)))
        
        # Create message as list of header, payload, and hash
        return pack('!1H' + str(len(payload)) + 's64s', self.msg_type.value, payload, datahash.digest())
    
    @staticmethod
    def deserialize(data, cipher):
        # Parse message
        # TODO: should check data before indexing into tuples
        msg_type = NodeMessages(unpack('!H', data[0:2])[0])
        payload = data[2:len(data)-64]
        datahash = data[len(data)-64:] # subtract hash size
        
        # Compute hash of encrypted data
        computed_hash = SHA512.new(payload)
        
        # Verify hash
        if computed_hash.digest() != datahash:
            return None
            
        # Decrypt message
        if cipher:
            payload = NodeMessage.decrypt_payload(payload, cipher)
        
        # Get payload dictionary
        payload_dict = json.loads(payload)
            
        return msg_type, payload_dict
    
def NodeMessageUnitTest():
    def generate_key():
        random_generator = Random.new().read
        key = RSA.generate(4096, random_generator)
        pvt=(key.publickey().n,key.publickey().e,key.d)
        pub=(key.publickey().n,key.publickey().e)
        
        return pub, pvt
    print('Generating keys')
    pub,pvt = generate_key()
    print('Constructing public key object')
    pubkey = RSA.construct(pub)
    print('Constructing private key object')
    pvtkey = RSA.construct(pvt)
    print('Constructing public cipher object')
    pubcipher = PKCS1_OAEP.new(pubkey)
    print('Constructing private cipher object')
    pvtcipher = PKCS1_OAEP.new(pvtkey)
    print('Creating message')
    msg_type = NodeMessages.JoinRequest
    payload_dict = { 'hi': 'hello' }
    msg = NodeMessage(msg_type, payload_dict, pubcipher)
    print('Serializing message')
    msgdata = msg.serialize()
    print('Deserializing message')
    recv_msg_type, recv_payload_dict = NodeMessage.deserialize(msgdata, pvtcipher)
    print('Checking payload consistency')
    print(recv_msg_type==msg_type)
    print(recv_payload_dict==payload_dict)