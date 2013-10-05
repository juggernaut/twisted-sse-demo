from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.protocols.basic import LineReceiver
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

EVENTSOURCE_URL = 'http://localhost:12000/subscribe'

class EventSourceProtocol(LineReceiver):
    def __init__(self, finished):
        self.finished = finished
        # Initialize the event and data buffers
        self.event = 'message'
        self.data = ''

    def lineReceived(self, line):
        if line == '':
            # Dispatch event
            self.dispatchEvent()
        else:
            try:
                field, value = line.split(':', 1)
                # If value starts with a space, strip it.
                value = lstrip(value)
            except ValueError:
                # We got a line with no colon, treat it as a field(ignore)
                return

            if field == '':
                # This is a comment; ignore
                pass
            elif field == 'data':
                self.data += value + '\n'
            elif field == 'event':
                self.event = value
            elif field == 'id':
                # Not implemented
                pass
            elif field == 'retry':
                # Not implemented
                pass

    def connectionLost(self, reason):
        self.finished.callback(None)

    def dispatchEvent(self):
        """
        Dispatch the event
        """
        # If last character is LF, strip it.
        if self.data.endswith('\n'):
            self.data = self.data[:-1]
        print "received event with payload %s and event type %s" % (self.data, self.event)
        self.data = ''
        self.event = 'message'

def lstrip(value):
    return value[1:] if value.startswith(' ') else value

agent = Agent(reactor)
d = agent.request(
    'GET',
    EVENTSOURCE_URL,
    Headers({
        'User-Agent': ['Twisted Web Client Example'],
        'Cache-Control': ['no-cache'],
        'Accept': ['text/event-stream; charset=utf-8'],
    }),
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
