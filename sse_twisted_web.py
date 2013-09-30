import sys

from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log

class Hello(resource.Resource):
    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        return "<html><body>Welcome to Twisted SSE</body></html>"

class Subscribe(resource.Resource):
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
        #return "<html>Hello, world!</html>"
        #request.write("data: hello world\r\n")
        #request.finish()
        return server.NOT_DONE_YET

    def publishToAll(self, data):
        for subscriber in self.subscribers:
            # NOTE: the second CRLF is required to dispatch the event at the client
            subscriber.write("data: %s\r\n\r\n" % data)

    def removeSubscriber(self, subscriber):
        if subscriber in self.subscribers:
            log.msg("Removing subscriber..")
            self.subscribers.remove(subscriber)

class Publish(resource.Resource):
    isLeaf = True

    def __init__(self, subscriber):
        self.subscriber = subscriber

    def render_POST(self, request):
        if 'data' not in request.args:
            request.setResponseCode(400)
            return "The parameter 'data' must be set\n"
        data = request.args.get('data')[0]
        self.subscriber.publishToAll(data)
        return 'Thank you for publishing data %s\n' % data

root = Hello()
subscribe = Subscribe()
root.putChild('subscribe', subscribe)
root.putChild('publish', Publish(subscribe))
site = server.Site(root)
reactor.listenTCP(12000, site)
log.startLogging(sys.stdout)
reactor.run()
