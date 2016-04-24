import json
from struct import *
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA512
from twisted.internet import reactor

from node_structure import node_methods
from NodeServer import NodeServer
from NodeClient import NodeClient

def generate_key():
    random_generator = Random.new().read
    key = RSA.generate(4096, random_generator)
    pvt=(key.publickey().n,key.publickey().e,key.d)
    pub=(key.publickey().n,key.publickey().e)
    
    return pub, pvt

def serialize_message(msg_type, payload_dict, key):
    # Create cipher from key
    cipher = PKCS1_OAEP.new(key)    # TODO: should this be created once and passed in?
    
    # Serialize message dictionary to JSON payload
    payload = json.dumps(payload_dict, indent=4, sort_keys=True)
    
    # Encrypt JSON payload
    encrypted_payload = cipher.encrypt(payload)
    
    # Compute hash of encrypted payload
    datahash = SHA512.new(bytes(str(encrypted_payload)))
    
    # Create message as list of header, payload, and hash
    return pack('!1H' + str(len(encrypted_payload)) + 's64s', msg_type, encrypted_payload, datahash.digest())
    
def deserialize_message(data, key):
    # Create cipher from key
    cipher = PKCS1_OAEP.new(key)    # TODO: should this be created once and passed in?

    # Parse message
    # TODO: should check data before indexing into tuples
    msg_type = unpack('!H', data[0:2])[0]
    encrypted_payload = data[2:len(data)-64]
    datahash = data[len(data)-64:] # subtract hash size
    
    # Compute hash of encrypted data
    computed_hash = SHA512.new(encrypted_payload)
    
    # Verify hash
    if computed_hash.digest() != datahash:
        return None
        
    # Decrypt message
    payload = cipher.decrypt(encrypted_payload)
    
    # Get payload dictionary
    payload_dict = json.loads(payload)
    
    return msg_type, payload_dict
    
def test():
    pub,pvt = generate_key()
    pubkey = RSA.construct(pub)
    pvtkey = RSA.construct(pvt)
    msg_type = 2
    payload_dict = { 'hi': 'hello' }
    msg = serialize_message(msg_type, payload_dict, pubkey)
    recv_msg_type, recv_payload_dict = deserialize_message(msg, pvtkey)
    print(recv_msg_type==msg_type)
    print(recv_payload_dict==payload_dict)

class TxValidateNode(node_methods):
    def __init__(self, cndsIp, cndsPort, localIp, localPort):
        self.reactor = reactor
        self.cnds = NodeClient(self.reactor, cndsIp, cndsPort)
        self.cnds.onConnect = self.cndsOnConnect
        self.cnds.onReceive = self.cndsDataReceived
        
        self.server = NodeServer(self.reactor, localIp, localPort, 10)
        self.server.onConnect = self.nodeOnConnect
        self.server.onReceive = self.nodeOnReceive
        
    def run(self):
        self.reactor.run()
        
    def cndsOnConnect(self, node, addr):
        return self.join_req()
        
    def cndsDataReceived(self, addr, data):
        if data == "approved":
            print("Join succeeded")
        elif data == "hello?":
            print("Pinged by CNDS")
            self.pingCount += 1
            return "hello"
        else:
            print("Join failed")
            
        return None

    def nodeOnConnect(self, node, addr):
        print("Connected to node at " + addrToStr(addr))
            
    def nodeOnReceive(self, addr, data):
        print("Received from node at " + addrToStr(addr) + ": " + data)

    
    
    




