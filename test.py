import sys
from sys import executable
from subprocess import * # CREATE_NEW_CONSOLE
from TxOriginNode import *
import subprocess

def main(args):
    cnds_info_path = "cnds_info.json"
    with open('node1_config.json','r') as datafile:
        node1_dict=json.load(datafile)
        
    with open('node2_config.json','r') as datafile:
        node2_dict=json.load(datafile)
    
    network_info = {
        "node1": node1_dict,
        "node2": node2_dict,
        #"node3": "node3_config.json"
    }
    
    #subprocess.Popen("airmon-ng check kill", shell=True)
    Popen([ 'CndsNodeTest.py', cnds_info_path], shell=True)
    
    for name, node_config_path in network_info.iteritems():
        Popen(['TxValidateNode.py', node_config_path], shell=True)
     
    execfile('TxOriginNode.py', cnds_info_path)   
    Popen(['TxOriginNode.py', cnds_info_path])

if __name__ == "__main__":
    main(sys.argv)