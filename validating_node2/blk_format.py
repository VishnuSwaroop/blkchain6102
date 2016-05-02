from Crypto.Hash import SHA512
from collections import *

      
class block_header:
    def __init__(self, blockconfig,merkle,prev_hash): #blockconfig is a dictionary or a json file
        self.version = blockconfig['version']
        self.previoushash = prev_hash
        self.merklehash = merkle
        self.time = None
        self.bits = blockconfig['bits']
        self.nonce = None
    
    def toString(self):
        print "Version: %d" % self.version
        print "Previous Hash %s" % str(self.previoushash)
        print "Merkle Root %s" % str(self.merklehash)
        print "Time %s" % str(self.time)
        print "Difficulty %8x" % self.bits
        print "Nonce %s" % str(self.nonce)
        
    def to_dict(self):
        dict_form={'version':self.version,
                   'previoushash':self.previoushash,
                   'merklehash':self.merklehash,
                   'time':self.time,
                   'bits':self.bits,
                   'nonce':self.nonce}
        return dict_form
        
        
class block_object:
    def __init__(self, blockconfig, tx_dict,prev_hash):
        
        tx_order_dict= OrderedDict(tx_dict)
        self.magicnum = (blockconfig['magicnum'])
        self.blocksize = None
        self.setHeader(blockconfig,tx_order_dict,prev_hash)
        self.txcount = len(tx_order_dict.keys()) #fixed no of transactions=8
        self.transactions=tx_order_dict
    
    def setHeader(self, blockconfig,tx_order_dict,prev_hash):
        merkle=self.set_merkle(tx_order_dict)
        self.blockHeader = block_header(blockconfig,merkle,prev_hash)
                
    
    def set_merkle(self,tx_order_dict):

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
        
        
            
    
    def toString(self):
        print ""
        print "Magic No: ",self.magicnum
        print "Blocksize: \t", self.blocksize
        print ""
        print "#"*10 + " Block Header " + "#"*10
        self.blockHeader.toString()
        print
        print "##### Tx Count: %d" % self.txcount
        i=0
        for t in self.transactions:
            print ('Transaction %d'% i)
            i=i+1
            print(str(self.transactions[t]))
            
    def to_dict(self):
        #         self.magicnum = (blockconfig['magicnum'])
        # self.blocksize = (blockconfig['blocksize'])
        # self.setHeader(blockconfig,tx_dict)
        # self.txcount = (8) #fixed no of transactions
        # self.transactions=tx_dict
    
        dict_form={'magicnum':self.magicnum,
                   'blocksize':self.blocksize,
                   'block_header': self.blockHeader.to_dict(),
                   'txcount':self.txcount,
                   'transactions':self.transactions}
        return dict_form