import time
import array, random, json
from random import randint
from twisted.internet import reactor, threads
from Crypto.Hash import *

class ProofOfWork:
        def __init__(self, reactor, block, completed_handler, failed_handler):
            self.reactor = reactor
            self.block = block
            self.nonce = None
            self.aborted = False
            self.completed_handler = completed_handler
            self.failed_handler = failed_handler
            
            self.deferred = threads.deferToThread(self.generate)
            self.deferred.addCallback(self.completed)
            self.deferred.addErrback(self.failed)
    
        @staticmethod
        def verify(prev_hash, header_hash, nonce, difficulty):
            """
            Verifies a hashcash token against 'prev_hash' with difficulty level 'difficulty'
            """	

            # mask is an int with least-significant 'q' bits set to 1
            mask = 2 ** difficulty - 1
            if not prev_hash:
                prev_hash = 128 * '0'
            # produce hash string and hash int for input string
            hV = prev_hash
            nHv = intify(hV)
        
            # hash the string and the token
            Tok = header_hash + str(nonce)
            hTok = SHA512.new(Tok).hexdigest()
            
            # defeat the obvious attack
            if hTok == hV:
                print "Rejecting token chunk - equal to token"
                return False
            
            # test if these hashes have the least significant n bits in common
            nHTok = intify(hTok)
            if (nHTok ^ nHv) & mask != 0:
                print '~~~~~~~~~~~~~~~~~ HASHCASH VERIFICATION FAILURE ~~~~~~~~~~~~~~~~'
                print "Rejecting token - hash test failed" 
                print "nHTok=%s - nHv=%s" % (nHTok, nHv)
                return False
            
            # pass
            print '~~~~~~~~~~~~~~~~~ HASHCASH VERIFICATION SUCCESS ~~~~~~~~~~~~~~~~'
            return True
    
        def generate(self):
            """
            Generate a hashcash token against string 'value'
            """
            block_dict=self.block.to_dict()
            prev_hash=block_dict['block_header']['previoushash']
            header_data=str(block_dict['magicnum']) +str(block_dict['block_header']['version'])+ str(block_dict['block_header']['merklehash'])+str(block_dict['block_header']['time'])+str(block_dict['txcount'])
            # difficulty=int(blockchain_state['prev_hash']['header']['difficulty']) #either add 1 to the latest difficulty value, or accept some global value)
            difficulty=12
            
            print("Starting proof of work")
            mask = 2 ** difficulty - 1
            # hV = sha.new(prev_hash).hexdigest()	# hash value

            if not prev_hash:
                prev_hash = 128 * '0'

            hV=prev_hash

            nHV = intify(hV)					# transform into int
            
            TokenSize = 3
            maxTokInt = 2 ** (TokenSize * 8)		# max possible value of a token
            
            self.nonce = 0
            
            while 1:
                if self.aborted:
                    print("Aborting proof of work thread")
                    return
                self.nonce += 1
                Tok = header_data + str(self.nonce)
                nTok = intify(Tok)
                sNTok = binify(nTok)
                hSNTok = SHA512.new(sNTok).hexdigest()
                nHSNTok = intify(hSNTok)
                if (nHV ^ nHSNTok) & mask == 0:
                    # got a good token
                    print '~~~~~~~~~~~~~~~~~ HASHCASH SUCCESS ~~~~~~~~~~~~~~~~'
                    # return "".join(sNTok)
                    return
                    
            print("Ending proof of work")
            
        def completed(self, ignored):
            print("Proof of work complete")
            self.reactor.callFromThread(self.completed_handler, self.block, self.nonce)
            
        def failed(self, failure):
            print("Proof of work failed")
            self.reactor.callFromThread(self.failed_handler, failure, self.block)
            
        def abort(self):
            print("Proof of work aborted")
            self.aborted = True     # proof of work thread must check this flag every iteration and abort if required
            self.deferred.pause()
            self.deferred.cancel()
            return self.block
            
def binify(L):
    """
    Convert a python long int into a binary string
    """
    res = []
    while L:
        res.append(chr(L & 0xFF))
        L >>= 8
    res.reverse()
    return "".join(res)

def intify(s):
    """
    Convert a binary string to a python long int
    """
    n = 0L
    for c in s:
        n = (n << 8) | ord(c)
    return n
    
# Unit Test    
if __name__ == "__main__":
    print("Proof of Work Unit Test")
    block = {"hello":"hi"}
    
    def completed(block, nonce):
        print("Completed:\n\tBlock: {0}\n\tNonce: {1}".format(str(block), str(nonce)))
    
    def failed(failure, block):
        print("Failed: {0}\n\tBlock: {1}".format(str(failure), str(block)))
    
    def create_and_abort(numpow, abort_time):
        print("Created POW (#{0})".format(numpow))
        p = ProofOfWork(reactor, block, completed, failed)
        if abort_time and abort_time > 0:
            time.sleep(abort_time)
            print("Aborted block: {0}".format(str(p.abort())))
        p = None
    
    time.sleep(5)
    reactor.callLater(0, create_and_abort, 1, 4)
    reactor.callLater(12, create_and_abort, 2, 3)
    reactor.callLater(20, create_and_abort, 3, 2)
    reactor.callLater(23, create_and_abort, 4, 2)
    reactor.callLater(29, create_and_abort, 5, 4)
    reactor.callLater(34, create_and_abort, 6, 0)
    reactor.run()
    
    print("Unit test complete")