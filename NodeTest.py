from NodeServer import NodeServer
from NodeClient import NodeClient

def main():
    print("Starting NodeTest")
    cndsClient = NodeClient("localhost", 1234)
    cndsClient.sendData("hello world")
    
if __name__ == "__main__":
    main()
    
    
    
    




