from twisted.web import server, resource
from twisted.internet import reactor, endpoints
from twisted.internet.endpoints import TCP4ServerEndpoint
from TxNodeUtil import *

class NodeServer(resource.Resource):
    isLeaf = True
    
    def __init__(self, local_port, local_ip):
        resource.Resource.__init__(self)
        self.reactor = reactor
        self.local_port = local_port
        self.local_ip = local_ip
        backlog = 10
        endpoint = TCP4ServerEndpoint(reactor, self.local_port, backlog, self.local_ip)
        endpoint.listen(server.Site(self))
        
    def render_response(self, request, handler):
        request.setHeader(b"content-type", b"application/octet-stream")
        
        fcn = request.uri[1:]
        
        # TODO: set the ciphers based on which node issued the request
        request_cipher = None   
        response_cipher = None
       
        request_str = request.content.getvalue()
        resp_str = None
        payload_dict = None
       
        #print("Request String: " + str(request_str))
        
        try:
            payload_dict = deserialize_payload(request_str, request_cipher)
        except:
            print("Failed to deserialize request:")
            print("\tFunction: " + str(fcn))
            print("\tRequest String: " + str(request_str))
        
        # The call to the handler should stay outside to allow crash if handler has error
        if payload_dict:
            resp_dict = handler(fcn, payload_dict)
            
            try:
                resp_str = serialize_payload(resp_dict, response_cipher)
            except:
                print("Failed to serialize response:")
                print("\tFunction: " + str(fcn))
                print("\tRequest Payload: " + str(payload_dict))
                print("\tResponse Payload: " + str(resp_dict))
            
        if resp_str:
            return resp_str
        else:
            request.setResponseCode(404)
            return "Unknown request"    # TODO: this should probably handle the JSON serialization of the payload and hash?
    
    def render_GET(self, request):
        print("GET request: " + request.uri)
        return self.render_response(request, self.handle_get)
        
    def render_POST(self, request):
        print("POST request: " + request.uri)
        return self.render_response(request, self.handle_post)