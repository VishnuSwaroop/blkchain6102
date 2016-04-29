import sys
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE
from TxOriginNode import *

def main(args):
    cnds_info_path = "cnds_info.json"
    
    network_info = {
        "node1": "node1_config.json",
        "node2": "node2_config.json",
        "node3": "node2_config.json",
    }
    
    Popen([executable, 'CndsNodeTest.py', cnds_info_path], creationflags=CREATE_NEW_CONSOLE)
    
    for name, node_config_path in network_info.iteritems():
        Popen([executable, 'TxValidateNode.py', node_config_path], creationflags=CREATE_NEW_CONSOLE)
     
    #execfile('TxOriginNode.py', cnds_info_path)   
    Popen([executable, 'TxOriginNode.py', cnds_info_path])

if __name__ == "__main__":
    main(sys.argv)