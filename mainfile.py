import random
import Crypto
import json
def main():
    with open('networkinput.json','r') as data_file:    
        networkdata = json.load(data_file)
    
    
    for dictkey in networkdata.keys():
        networkdata[dictkey]["nodepvtkey"]=tuple(networkdata[dictkey]["nodepvtkey"])
        networkdata[dictkey]["nodepubkey"]=tuple(networkdata[dictkey]["nodepubkey"])
        networkdata[dictkey]["CNDSpubkey"]=tuple(networkdata[dictkey]["CNDSpubkey"])
        #networkdata[dictkey]["CNDSpvtkey"]=tuple(networkdata[dictkey]["CNDSpvtkey"])
        
    print('THE TYPE OF KEY INFO IS:::')
    print(type(networkdata["n1"]["nodepvtkey"]))
    
    
    #print (networkdata)
    listofcreatednodes=[]
    print()
    print()
    #node1=new_TXvalidation_node()
    for i in range (5):
        new_node=new_TXvalidation_node(infodict=networkdata)
        while(new_node in listofcreatednodes):
            new_node=new_TXvalidation_node(infodict=networkdata)
    
        listofcreatednodes.append(new_node)
    
    
    
    
    print('The nodes are: ')
    print (listofcreatednodes)
    print()
    print()
    print('An example objects pvt key type is :')
    print(type(listofcreatednodes[2].nodepvtkey))
    print(type(listofcreatednodes[2].CNDSpubkey))


class new_TXvalidation_node:
    #def __init__(self,nodename,CNDSdomname,CNDSip,CNDSpubkey,nodeip,nodepubkey,nodepvtkey,online=False):
    def __init__(self,infodict,nodename='',CNDSdomname='',CNDSip='',CNDSpubkey=(),nodeip='',nodepubkey=(),nodepvtkey=(),online=False):
    
        # 
        # nodedict={"nodename":infodict[i],
        #           "CNDSdomname": infodict[i][CNDSdomname],
        #           "CNDSip": infodict[i][CNDSip],
        #           "CNDSpubkey": infodict[i][CNDSpubkey],
        #           "nodeip": infodict[i][nodeip],
        #           "nodepubkey": infodict[i][nodepubkey],
        #           "nodepvtkey": infodict[i][nodepvtkey]}
        
        
        #nodedictjson=json.dump(nodedict, indent=4,sort_keys=True)
        self.nodename=nodename
        self.CNDSdomname=CNDSdomname
        self.CNDSip= CNDSip
        self.CNDSpubkey= CNDSpubkey
        self.nodeip=nodeip
        self.nodepubkey=nodepubkey 
        self.nodepvtkey=nodepvtkey
        self.online=online
        
        self.createnode(infodict)
        
    def createnode(self, infodict):
        # print('Infodict is::::')
        # print(infodict)
        i=random.randint(0,10) 
        i="n"+str(i)
        self.nodename=infodict[i],
        self.CNDSdomname=infodict[i]["CNDSdomname"]
        self.CNDSip= infodict[i]["CNDSip"]
        self.CNDSpubkey= infodict[i]["CNDSpubkey"]
        self.nodeip=infodict[i]["nodeip"]
        self.nodepubkey= infodict[i]["nodepubkey"]
        self.nodepvtkey= infodict[i]["nodepvtkey"]
        
        #return new_TXvalidation_node()






if __name__ == '__main__':
    main()