from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, HTTPConnectionPool

class BasicProtocol(Protocol):
    def __init__(self, deferred):
        self.deferred = deferred

    def dataReceived(self, bytes):
        print(bytes)

    def connectionLost(self, reason):
        self.deferred.callback(None)


def cbRequest(response):
    print 'Response code: ', response.code
    finished = Deferred()
    response.deliverBody(BasicProtocol(finished))
    return finished

pool = HTTPConnectionPool(reactor)
agent = Agent(reactor, pool=pool)

def requestGet(url):
    d = agent.request('GET', url)
    d.addCallback(cbRequest)
    return d

# Two requests to the same host:
d = requestGet('http://localhost:8080/request1').addCallback(
    lambda ign: requestGet("http://localhost:8080/request2"))
def cbShutdown(ignored):
    reactor.stop()
d.addCallback(cbShutdown)

reactor.run()