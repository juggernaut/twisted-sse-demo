from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.protocols.basic import LineReceiver
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

EVENTSOURCE_URL = 'http://localhost:12000/subscribe'

class EventSourceProtocol(LineReceiver):
    def __init__(self, finished):
        self.finished = finished
        self.buffer = ''

    def lineReceived(self, line):
        print 'Received line %s!' % line
        if line == '':
            # Dispatch event
            print "received event with payload %s" % self.buffer
            self.buffer = ''
        else:
            try:
                event, payload = line.split(':', 1)
            except ValueError:
                print 'protocol violation'
                self.finished.errback('protocol violation')
                return

            print 'buffering data!'
            self.buffer += payload

    def connectionLost(self, reason):
        self.finished.callback(None)

agent = Agent(reactor)
d = agent.request(
    'GET',
    EVENTSOURCE_URL,
    Headers({'User-Agent': ['Twisted Web Client Example']}),
    None)

def cbRequest(response):
    print 'Response version:', response.version
    print 'Response code:', response.code
    print 'Response phrase:', response.phrase
    print 'Response headers:'
    finished = Deferred()
    response.deliverBody(EventSourceProtocol(finished))
    return finished
d.addCallback(cbRequest)

def cbShutdown(ignored):
    reactor.stop()
d.addBoth(cbShutdown)

reactor.run()
