# Important aspects taken from http://freenet.mcnabhosting.com/python/hashcash/hashcash.py

from Crypto.Hash import *
import sha, array, random, json
from random import randint

shanew = SHA512.new

defaultTokenSize = 3        # size of each chunk in a token
defaultDifficulty = 12         # number of partial hash collision bits required

class HashCash:
    
    TokenSize = defaultTokenSize			# in bytes
    difficulty = defaultDifficulty 			# nb of bits the two hash have to match upon
    
    def __init__(self, **kw):
        """
        Create a HashCash object
        """
        for key in ['TokenSize', 'difficulty']:
            if kw.has_key(key):
                setattr(self, key, kw[key])
    
    def generate(self, prev_hash, header_hash, difficulty):
        """
        Generate a hashcash token against string 'value'
        """
        mask = 2 ** self.difficulty - 1
        # hV = sha.new(prev_hash).hexdigest()	# hash value
        hV=prev_hash
        nHV = intify(hV)					# transform into int
        
        maxTokInt = 2 ** (self.TokenSize * 8)		# max possible value of a token
        
        nonce = 0
		
        while 1:
            nonce += 1
            Tok = header_hash + str(nonce)
            nTok = intify(Tok)
            sNTok = binify(nTok)
            hSNTok = shanew(sNTok).hexdigest()
            nHSNTok = intify(hSNTok)
            if (nHV ^ nHSNTok) & mask == 0:
                # got a good token
                print '~~~~~~~~~~~~~~~~~ HASHCASH SUCCESS ~~~~~~~~~~~~~~~~'
                return nonce
                # return "".join(sNTok)
    
    def verify(self, prev_hash, header_hash, nonce, difficulty):
        """
        Verifies a hashcash token against 'prev_hash' with difficulty level 'difficulty'
        """	

        # mask is an int with least-significant 'q' bits set to 1
        mask = 2 ** self.difficulty - 1
    
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
            print "Rejecting token %s - hash test failed" % repr(token)
            print "nHTok=%s - nHv=%s" % (nHTok, nHv)
            return False
        
        # pass
        return True
    

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

def _randomString():
    """
    For our tests below.
    Generates a random-length human-readable random string,
    between 16 and 80 chars
    """
    chars = []
    slen = randint(16, 80)
    for i in range(slen):
        chars.append(chr(randint(32, 128)))
    value = "".join(chars)
    return value

def test(difficulty):

    print "Test of the HashCash function"

    prev_hash = _randomString()
	
    header_hash = _randomString()
	
    print "Generated random string for prev_hash :\n%s" % prev_hash
    print "Generated random string for header_hash :\n%s" % header_hash 

    hc = HashCash(difficulty=difficulty)

    print "Generating token for %s-bit partial collision." % difficulty
    nonce = hc.generate(prev_hash, header_hash, difficulty)

    print "Got nonce %s, now verifying" % repr(nonce)
    result = hc.verify(prev_hash, header_hash, nonce, difficulty)

    print "Verify = %s" % repr(result)
    print
	
def statistics(difficulty):

    hc = HashCash(difficulty=difficulty)
	
    nonces = []
	
    for i in range(100):
        prev_hash = _randomString()
        header_hash = _randomString()
        nonce = hc.generate(prev_hash, header_hash, difficulty)
        nonces.append(nonce)
		
    print repr(nonces)
	
    return nonces


