import sys
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE
from TxOriginNode import *

def main(args):
    cnds_ip = "localhost"
    cnds_port = 1234
    
    network_info = {
        "node1": { "node_ip": "localhost", "node_port": "1235", "node_pubkey": None },
        "node2": { "node_ip": "localhost", "node_port": "1236", "node_pubkey": None },
    }
    
    Popen([executable, 'CndsNodeTest.py', str(cnds_ip), str(cnds_port)], creationflags=CREATE_NEW_CONSOLE)
    
    for name, node in network_info.iteritems():
        Popen([executable, 'TxValidateNode.py', str(node["node_ip"]), str(node["node_port"])], creationflags=CREATE_NEW_CONSOLE)
     
    execfile('TxOriginNode.py')   
    #Popen([executable, 'TxOriginNode.py'])

if __name__ == "__main__":
    main(sys.argv)