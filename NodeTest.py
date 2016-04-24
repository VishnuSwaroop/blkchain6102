import sys
from TxValidateNode import *

def main(args):
    cndsIp = "localhost"
    cndsPort = 1234
    localIp = "localhost"
    localPort = 1235
    
    numArgs = len(args)
    if numArgs == 5:
        cndsIp = args[1]
        cndsPort = int(args[2])
        localIp = args[3]
        localPort = int(args[4])
    
    print("Starting NodeTest")
    node = TxValidateNode(cndsIp, cndsPort, localIp, localPort)
    node.createnode(localIp, cndsIp)
    node.run()
    
if __name__ == "__main__":
    main(sys.argv)
    
    
    
    




