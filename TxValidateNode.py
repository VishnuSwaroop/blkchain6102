import sys
from twisted.web import server, resource
from twisted.internet import reactor, endpoints
from twisted.internet.endpoints import TCP4ServerEndpoint
from TxNodeUtil import *

class TxValidateNode(resource.Resource):
    isLeaf = True

    def __init__(self, cnds_ip, local_port, local_ip):
        resource.Resource.__init__(self)
        self.reactor = reactor
        self.local_port = local_port
        self.local_ip = local_ip
        backlog = 10
        endpoint = TCP4ServerEndpoint(reactor, self.local_port, backlog, self.local_ip)
        endpoint.listen(server.Site(self))
        print("Node listening for connections on " + addr_port_to_str(self.local_ip, self.local_port))
        
    def run(self):
        self.reactor.run()
    
    def handle_get(self, uri, payload_dict, hash):
        print("GET " + uri + "\nPayload: " + str(payload_dict) + "\nHash: " + str(hash))
        if uri == "block":
            resp_dict = self.handle_block_lookup(payload_dict)
            
        return resp_dict
        
    def handle_post(self, uri, payload_dict, hash):
        print("POST " + uri + "\nPayload: " + str(payload_dict) + "\nHash: " + str(hash))
        if uri == "transaction":
            resp_dict = self.handle_add_tx(payload_dict)
        elif uri == "block":
            resp_dict = self.handle_add_block(payload_dict)
        
    def render_response(self, request, handler):
        request.setHeader(b"content-type", b"text/plain")
        
        uri = request.uri[2:]
        
        # TODO: set the ciphers based on which node issued the request
        request_cipher = None   
        response_cipher = None
       
        resp = None
        payload = None
        hash = None
        
        if "payload" in request.args:
            payload = request.args["payload"]
        if "hash" in request.args:    
            hash = request.args["hash"]
            
        if payload and hash:
            payload_dict = None
            
            try:
                payload_dict = deserialize_payload(payload, hash, request_cipher)
            except:
                print("Failed to deserialize request:")
                print("URI: " + str(uri))
                print("Request Payload: " + str(payload))
                print("Request Hash: " + str(hash))
            
            # The call to the handler should stay outside to allow crash if handler has error
            if payload_dict:
                resp_dict = handler(uri, payload_dict, hash)
                
                try:
                    resp = serialize_payload(resp_dict, response_cipher)
                except:
                    print("Failed to serialize response:")
                    print("URI: " + str(uri))
                    print("Request Payload: " + str(payload_dict))
                    print("Request Hash: " + str(hash))
                    print("Response Payload: " + str(resp_dict))
            
        if resp:
            return resp
        else:
            request.setResponseCode(404)
            return "Unknown request"
    
    def render_GET(self, request):
        return self.render_response(request, self.handle_get)
        
    def render_POST(self, request):
        return self.render_response(request, self.handle_post)

def main(args):
    cnds_ip = "localhost"
    local_ip = "localhost"
    local_port = 1235
    
    # Parse command line arguments
    for arg in args[1:]:
        if arg.isdigit():
            local_port = int(arg)
        else:
            print("Unknown argument: ", arg)
    
    # Run server
    print("Starting Transaction Validation Node service")
    node = TxValidateNode(cnds_ip, local_port, local_ip)
    node.run()

if __name__ == "__main__":
    main(sys.argv)