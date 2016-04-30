from Crypto.Hash import SHA512

class tx_object:
    def __init__(self, origin, owner,value, owner_pubkey,upper_limit, previous_hash=None, current_hash=None):
        self.previous_hash=previous_hash #generating new transactions and assigning this value is left to the user application, should be the prev tx's hash with all values
        self.origin=origin
        self.owner=owner
        self.owner_pubkey=owner_pubkey
        self.value=value
        self.upper_limit=upper_limit
        temp=str(self.previous_hash)+str(self.origin)+str(self.owner)+str(self.owner_pubkey)+str(self.value)+str(self.upper_limit)
        
        temp=SHA512.new(bytes(temp))
        self.current_hash=temp.hexdigest()
        
    def  to_string(self):
        print ''
        print '************************************************************************************'
        print 'TRANSACTION'
        print 'Previous Tx Hash : '+str(self.previous_hash)
        print 'Origin : '+str(self.origin)
        print 'Owner : '+str(self.owner)
        print 'Owner Public Key : '+str(self.owner_pubkey)
        print 'Value : '+str(self.value)
        print 'Upper Bound : '+str(self.upper_limit)
        print 'Current Hash : '+str(self.current_hash)
        print '***********************************************************************************'
    
    
    def to_dict(self):
        return {'previous_hash':self.previous_hash, #this is another dict
                'origin':str(self.origin),
                'owner':str(self.owner),
                'owner_pubkey':str(self.owner_pubkey),
                'value':str(self.value),
                'upper_limit':str(self.upper_limit),
                'current_hash':str(self.current_hash)}
    
