from threading import Thread

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
        agent = Agent(reactor)
        d = agent.request(
            'GET',
            self.url,
            Headers({
                'User-Agent': ['Twisted SSE Client'],
                'Cache-Control': ['no-cache'],
                'Accept': ['text/event-stream; charset=utf-8'],
            }),
            None)
        d.addCallback(self.cbRequest)
        d.addBoth(self.cbShutdown)

    def cbRequest(self, response):
        finished = Deferred()
        self.protocol.setFinishedDeferred(finished)
        response.deliverBody(self.protocol)
        return finished

    def cbShutdown(self, ignored):
        if reactor.running:
            reactor.stop()

    def onmessage(self, func):
        self.protocol.addCallback('message', func)

    def addEventListener(self, event, func):
        self.protocol.addCallback(event, func)

    def start(self):
        # Fire up the reactor in another thread.
        Thread(target=reactor.run, args=(False,)).start()

    def stop(self):
        reactor.callFromThread(self.cbShutdown, None)
