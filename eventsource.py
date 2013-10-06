from sse_client import EventSourceProtocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

class EventSource(object):
    """
    The main EventSource class
    """
    def __init__(self, url):
        self.url = url
        self.protocol = EventSourceProtocol()
        self.connect()

    def connect(self):
        """
        Connect to the event source URL
        """
        print 'connecting....'
        agent = Agent(reactor)
        d = agent.request(
            'GET',
            self.url,
            Headers({
                'User-Agent': ['Twisted Web Client Example'],
                'Cache-Control': ['no-cache'],
                'Accept': ['text/event-stream; charset=utf-8'],
            }),
            None)
        d.addCallback(self.cbRequest)
        d.addBoth(self.cbShutdown)

    def cbRequest(self, response):
        print 'Response version:', response.version
        print 'Response code:', response.code
        print 'Response phrase:', response.phrase
        print 'Response headers:'
        finished = Deferred()
        self.protocol.setFinishedDeferred(finished)
        response.deliverBody(self.protocol)
        return finished

    def cbShutdown(self, ignored):
        reactor.stop()

    def onmessage(self, func):
        self.protocol.addCallback('message', func)

    def addEventListener(self, event, func):
        self.protocol.addCallback(event, func)

def onmessage(data):
    print 'Got payload with data %s' % data

if __name__ == '__main__':
    EVENTSOURCE_URL = 'http://localhost:12000/subscribe'
    eventSource = EventSource(EVENTSOURCE_URL)
    eventSource.onmessage(onmessage)
    reactor.run()
