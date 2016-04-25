import sys
from TxValidateNode import *

def main(args):

    generate = False
    node_config_path = "node_config.json"
    cnds_info_path = "cnds_info.json"
   
    for arg in args[1:]:
        if arg == "gen":
            generate = True
        else:
            node_config_path = arg
        
    # Generate node ID
    if generate:
        print("Generating Node configuration")
        TxValidateNode.generate_node_config(node_config_path, "localhost", 1234)
    
    print("Starting Node")
    node = TxValidateNode(node_config_path, cnds_info_path)
    node.run()
    
if __name__ == "__main__":
    main(sys.argv)
    
    
    
    




