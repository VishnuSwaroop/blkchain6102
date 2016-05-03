import json

def global_hash_table(tx): #tx is a dict
    #to check if the node's previous tx's hash is present in the database
    #if yes, check for previous tx hash and return True if present (and update hash table) else return False
    with open('global_tx_hash.json','r') as datafile:
        tx_hashtable=json.load(datafile)
        
    
    if not tx_hashtable.get(tx['owner']):
        tx_hashtable[tx['owner']]=tx['current_hash']
        print 'Transaction added to global hash table'
        with open('global_tx_hash.json','w') as outfile:
            json.dump(tx_hashtable,outfile,indent=4,sort_keys=True)
        return True
    elif tx_hashtable.get(tx['owner']):
        if tx_hashtable[tx['owner']] == tx['previous_hash']:
            tx_hashtable[tx['owner']] = tx['current_hash']
            with open('global_tx_hash.json','w') as outfile:
                json.dump(tx_hashtable,outfile,indent=4,sort_keys=True)
            print 'Global hash table updated'
            
            return True
        
        else:
            print ("**** Invalid Transaction ***  Previous transaction's hash from node %s does not match records" %str(tx['owner']))
            return False
        
    else:
        print "Something went wrong in global hash table"
            