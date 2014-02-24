from crochet import setup, run_in_reactor
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

from sse_client import EventSourceProtocol

setup()


class EventSource(object):
    """
    The main EventSource class
    """
    def __init__(self, url):
        self.url = url
        self.protocol = EventSourceProtocol()
        self.errorHandler = None
        self.stashedError = None
        self.connect()

    @run_in_reactor
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
        d.addErrback(self.connectError)
        d.addCallback(self.cbRequest)

    def cbRequest(self, response):
        if response.code != 200:
            self.callErrorHandler("non 200 response received: %d" %
                                  response.code)
        else:
            finished = Deferred()
            self.protocol.setFinishedDeferred(finished)
            response.deliverBody(self.protocol)
            return finished

    def connectError(self, ignored):
        self.callErrorHandler("error connecting to endpoint: %s" % self.url)

    def callErrorHandler(self, msg):
        if self.errorHandler:
            func, callInThread = self.errorHandler
            if callInThread:
                reactor.callInThread(func, msg)
            else:
                func(msg)
        else:
            self.stashedError = msg

    def onerror(self, func, callInThread=False):
        self.errorHandler = func, callInThread
        if self.stashedError:
            self.callErrorHandler(self.stashedError)

    def onmessage(self, func, callInThread=False):
        self.addEventListener('message', func, callInThread)

    def addEventListener(self, event, func, callInThread=False):
        callback = func
        if callInThread:
            callback = lambda data: reactor.callInThread(func, data)
        self.protocol.addCallback(event, callback)
