from twisted.web import server, resource
from twisted.internet import reactor, endpoints
from twisted.internet.endpoints import TCP4ServerEndpoint

from TxNodeUtil import *
from NodeInfo import *

class NodeServer(resource.Resource):
    isLeaf = True
    
    def __init__(self, local_info):
        resource.Resource.__init__(self)
        self.reactor = reactor
        self.local_info = local_info
        backlog = 10
        endpoint = TCP4ServerEndpoint(reactor, self.local_info.port, backlog, self.local_info.ip)
        endpoint.listen(server.Site(self))
        
    def render_response(self, request, handler):
        request.setHeader(b"content-type", b"application/octet-stream")
        
        client_ip = request.getClientIP()
        
        fcn = request.uri[1:]
        
        # TODO: set the ciphers based on which node issued the request
        request_cipher = None
        response_cipher = None
       
        request_str = request.content.getvalue()
        resp_str = None
        payload_dict = None
       
        #print("Request String: " + str(request_str))
        
        try:
            if request_str:
                print("Request String: {0}".format(request_str))
                payload_dict, client_info = deserialize_payload(json.loads(request_str), request_cipher)
                client_info.ip = client_ip
            else:
                payload_dict = None
                client_info = None
            
        except:
            print("Failed to deserialize request:")
            print("\tFunction: " + str(fcn))
            print("\tRequest String: " + str(request_str))
            raise
        
        # The call to the handler should stay outside to allow crash if handler has error
        #if payload_dict:
        resp_dict = handler(fcn, payload_dict, client_info)
        
        try:
            resp_str = serialize_payload(resp_dict, None, response_cipher)
        except:
            print("Failed to serialize response:")
            print("\tFunction: " + str(fcn))
            print("\tRequest Payload: " + str(payload_dict))
            print("\tResponse Payload: " + str(resp_dict))
            raise
            
        if resp_str:
            return resp_str
        else:
            request.setResponseCode(404)
            return "Unknown request"   
    
    def render_GET(self, request):
        #print("GET request: " + request.uri)
        return self.render_response(request, self.handle_get)
        
    def render_POST(self, request):
        #print("POST request: " + request.uri)
        return self.render_response(request, self.handle_post)