import sys

from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log


class Root(resource.Resource):
    """
    Root resource; serves JavaScript
    """
    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        return r"""
        <html>
            <head>
                <script language="JavaScript">
                        eventSource = new EventSource("http://localhost:12000/subscribe");
                        eventSource.onmessage = function(event) {
                            element = document.getElementById("event-data");
                            element.innerHTML = event.data;
                        };
                    </script>
            </head>
            <body>
                <h1> Welcome to the SSE demo </h1>
                <h3> Event data: </h3>
                <p id="event-data"></p>
            </body>
        </html>
        """


class Subscribe(resource.Resource):
    """
    Implements the subscribe resource
    """
    isLeaf = True

    def __init__(self):
        self.subscribers = set()

    def render_GET(self, request):
        request.setHeader('Content-Type', 'text/event-stream; charset=utf-8')
        request.setResponseCode(200)
        self.subscribers.add(request)
        d = request.notifyFinish()
        d.addBoth(self.removeSubscriber)
        log.msg("Adding subscriber...")
        request.write("")
        return server.NOT_DONE_YET

    def publishToAll(self, data):
        for subscriber in self.subscribers:
            for line in data:
                subscriber.write("data: %s\r\n" % line)
            # NOTE: the last CRLF is required to dispatch the event at the client
            subscriber.write("\r\n")

    def removeSubscriber(self, subscriber):
        if subscriber in self.subscribers:
            log.msg("Removing subscriber..")
            self.subscribers.remove(subscriber)


class Publish(resource.Resource):
    """
    Implements the publish resource
    """
    isLeaf = True

    def __init__(self, subscriber):
        self.subscriber = subscriber

    def render_POST(self, request):
        if 'data' not in request.args:
            request.setResponseCode(400)
            return "The parameter 'data' must be set\n"
        data = request.args.get('data')
        self.subscriber.publishToAll(data)
        return 'Thank you for publishing data %s\n' % '\n'.join(data)


root = Root()
subscribe = Subscribe()
root.putChild('subscribe', subscribe)
root.putChild('publish', Publish(subscribe))
site = server.Site(root)
reactor.listenTCP(12000, site)
log.startLogging(sys.stdout)
reactor.run()
