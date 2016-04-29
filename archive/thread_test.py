from twisted.internet import reactor
import time

def short_op():
    print("Starting short op")
    time.sleep(2)
    print("Done with short op")
    
def long_op():
    print("Starting long op")
    time.sleep(5)
    print("Done with long op")

# run method in thread
reactor.callFromThread(long_op)
reactor.callInThread(short_op)
reactor.run()