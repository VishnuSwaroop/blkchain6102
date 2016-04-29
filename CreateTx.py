import sys
from TxOriginNode import *

def main(args):
    get = None
    cnds_info_path = None
    
    # Parse command line arguments
    for arg in args[1:]:
        
        if arg == "get":
            get = True
        elif get:
            cnds_info_path = arg
    
    # Load CNDS configuration
    if cnds_info_path:
        cnds_info = load_cnds_config(cnds_info_path)
    
    # Run server
    print("Starting Node")
    # try:
    txs = []
    for i in xrange(1, 5*2):
        txs.append({"tx{0}".format(i): "txinfo"})
    node = TxOriginNode(cnds_info, txs)
    node.start()
    # except Exception as exc:
    #   print("Fatal Error: " + str(exc))

if __name__ == "__main__":
    main(sys.argv)