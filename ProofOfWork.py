import time
from twisted.internet import reactor, threads

class ProofOfWork:
        def __init__(self, reactor, block, completed_handler, failed_handler):
            self.reactor = reactor
            self.block = block
            self.nonce = None
            self.aborted = False
            self.completed_handler = completed_handler
            self.failed_handler = failed_handler
            self.deferred = threads.deferToThread(self.perform)
            self.deferred.addCallback(self.completed)
            self.deferred.addErrback(self.failed)
    
        def perform(self):
            print("Starting proof of work")
            for i in xrange(1, 10):
                time.sleep(1)  # TODO: replace with hashcash
                if self.aborted:
                    print("Aborting proof of work thread")
                    return None
            print("Work proven!")
            self.nonce = 2
            # raise Exception("whhhhhy!!!?")
            print("Ending proof of work")
            
        def completed(self, ignored):
            print("Proof of work complete")
            self.reactor.callFromThread(self.completed_handler, self.block, self.nonce)
            
        def failed(self, failure):
            print("Proof of work failed")
            self.reactor.callFromThread(self.failed_handler, failure, self.block)
            
        def abort(self):
            print("Proof of work aborted")
            self.aborted = True     # proof of work thread must check this flag every iteration and abort if required
            self.deferred.pause()
            self.deferred.cancel()
            return self.block
    
# Unit Test    
if __name__ == "__main__":
    print("Proof of Work Unit Test")
    block = {"hello":"hi"}
    
    def completed(block, nonce):
        print("Completed:\n\tBlock: {0}\n\tNonce: {1}".format(str(block), str(nonce)))
    
    def failed(failure, block):
        print("Failed: {0}\n\tBlock: {1}".format(str(failure), str(block)))
    
    def create_and_abort(numpow, abort_time):
        print("Created POW (#{0})".format(numpow))
        p = ProofOfWork(reactor, block, completed, failed)
        if abort_time and abort_time > 0:
            time.sleep(abort_time)
            print("Aborted block: {0}".format(str(p.abort())))
        p = None
    
    time.sleep(5)
    reactor.callLater(0, create_and_abort, 1, 4)
    reactor.callLater(12, create_and_abort, 2, 3)
    reactor.callLater(20, create_and_abort, 3, 2)
    reactor.callLater(23, create_and_abort, 4, 2)
    reactor.callLater(29, create_and_abort, 5, 4)
    reactor.callLater(34, create_and_abort, 6, 0)
    reactor.run()
    
    print("Unit test complete")