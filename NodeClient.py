from twisted.internet import reactor, endpoints, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.defer import succeed
from twisted.web.client import Agent, HTTPConnectionPool
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import implements

from TxNodeUtil import *
from NodeInfo import *

class NodeClient:
    @staticmethod
    def create_request(sender_info, recipient_info, method, fcn, req_dict, resp_handler, req_cipher=None, resp_cipher=None, timeout=2.0):
        client = NodeClient(timeout)
        client.send_request(sender_info, recipient_info, method, fcn, req_dict, resp_handler, req_cipher, resp_cipher)
        
    @staticmethod
    def run():
        reactor.run()
    
    def __init__(self, connectTimeout):
        
        # Use global connection pool to persist TCP connections for this process
        if not hasattr(NodeClient, "_connection_pool"):
            NodeClient._connection_pool = HTTPConnectionPool(reactor)
        
        self.reactor = reactor
        self.agent = Agent(self.reactor, connectTimeout=connectTimeout, pool=NodeClient._connection_pool)
        # print("Agent connect timeout: {0}".format(connectTimeout))
        
    def send_request(self, sender_info, recipient_info, method, fcn, request_dict, response_handler, request_cipher, response_cipher):
        class StringProducer(object):
            implements(IBodyProducer)
            
            def __init__(self, body):
                self.body = body
                self.length = len(body)
        
            def startProducing(self, consumer):
                consumer.write(self.body)
                return succeed(None)
        
        sender_info_dict = None
        if sender_info:
            sender_info_dict = sender_info.get_dict()
        payload_dict = { "sender": sender_info_dict, "payload": request_dict }
        request_str = serialize_payload(payload_dict, request_cipher)
        # print("Sending request: " + str(request_str))
        
        body = StringProducer(request_str)
        res = self.agent.request(
            method,
            "http://{0}/{1}".format(recipient_info.get_uri(), fcn),
            Headers({'User-Agent': ['TxNodeClient'], 'Content-Type': ['application/octet-stream']}),
            body)
        
        #print("Sending request and waiting for response")
        res.addCallback(self.get_resp, response_cipher, response_handler)
        res.addErrback(self.get_fail, response_handler)
        
    def get_resp(self, response, response_cipher, response_handler):
        #print("Request complete")

        # print("Good response: " + str(response))
        class DeliveryProtocol(protocol.Protocol):
            def __init__(self, response_handler, cipher):
                self.response_handler = response_handler
                self.cipher = cipher
            
            def dataReceived(self, resp):
                #print("Receiving data: " + resp)
                
                resp_dict = deserialize_payload(resp, self.cipher)
                
                response_handler(resp_dict, None)
        
        response.deliverBody(DeliveryProtocol(response_handler, response_cipher))
            
    def get_fail(self, fail, response_handler):
            # Parse failure
            #print("Failure: " + str(fail))
            response_handler(None, fail)
            