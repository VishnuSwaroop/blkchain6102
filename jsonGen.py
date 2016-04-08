import json
import random
from Crypto.PublicKey import RSA
from Crypto import Random

listofkeys=[]
for i in range(10):
    random_generator = Random.new().read
    key1 = RSA.generate(1024, random_generator)
    listofkeys.append(key1)

#<_RSAobj @0x7f60cf1b57e8 n(1024),e,d,p,q,u,private>
random_generator = Random.new().read
cnds_key = RSA.generate(1024, random_generator)
CNDSpvtkey=(cnds_key.publickey().n,cnds_key.publickey().e,cnds_key.d)
#print(type(nodepvtkey))
CNDSpubkey=(cnds_key.publickey().n,cnds_key.publickey().e)

CNDSdomname="leader1"

#from pprint import pprint

CNDSip=random.sample(range(0, 255), 4)
CNDSip=[str(i) for i in CNDSip]
CNDSip='.'.join(CNDSip)


CNDSpvtDict={"CNDSpvtkey":CNDSpvtkey}

nodeips=[]
for i in range(10):
    nodeip=random.sample(range(0, 255), 4)
    nodeip=[str(i) for i in nodeip]
    nodeip='.'.join(nodeip)
    nodeips.append(nodeip)


ntwkdata={}

for i in range(10):
    n="n"+str(i)
    nodepvtkey=(listofkeys[i].publickey().n,listofkeys[i].publickey().e,listofkeys[i].d)
    #print(type(nodepvtkey))
    nodepubkey=(listofkeys[i].publickey().n,listofkeys[i].publickey().e)
    #print(type(nodepubkey))
    ntwkdata[n]={"CNDSdomname":CNDSdomname,"CNDSip":CNDSip,"CNDSpubkey":CNDSpubkey,"nodepvtkey":nodepvtkey,"nodeip":nodeips[i],"nodepubkey":nodepubkey}



with open('networkinput.json', 'w') as outfile:
    json.dump(ntwkdata, outfile, indent=4,sort_keys=True)
   
    


with open('CNDSpvtkey.json', 'w') as outfile:
    json.dump(CNDSpvtDict, outfile, indent=4, sort_keys=True)
   

#TO GET BACK THE JSON DATA USE THE BELOW CODE

# with open('networkinput.json','r') as data_file:    
#     data = json.load(data_file)
# 
# 
# for dictkey in data.keys():
#     data[dictkey]["nodepvtkey"]=tuple(data[dictkey]["nodepvtkey"])
#     data[dictkey]["nodepubkey"]=tuple(data[dictkey]["nodepubkey"])
#     
# print('THE TYPE OF KEY INFO IS:::')
# print(type(data["n1"]["nodepvtkey"]))