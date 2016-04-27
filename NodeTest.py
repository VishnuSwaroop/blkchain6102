import sys
from TxValidateNode import *

def main(args):

    generate = False
    node_config_path = "node_config.json"
    cnds_info_path = "cnds_info.json"
    port_override = None
   
    for arg in args[1:]:
        if arg == "gen":
            generate = True
        elif arg.isdigit():
            port_override = int(arg)
        else:
            node_config_path = arg
        
    # Generate node ID
    if generate:
        print("Generating Node configuration")
        TxValidateNode.generate_node_config(node_config_path, "localhost", 1234)
    
    print("Starting Node")
    node = TxValidateNode(node_config_path, cnds_info_path, port_override)
    node.run()
    
if __name__ == "__main__":
    main(sys.argv)
    
    




