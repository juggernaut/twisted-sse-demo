import time

from eventsource import EventSource

EVENTSOURCE_URL = 'http://localhost:12000/subscribe'

def onmessage(data):
    print 'Got payload with data %s' % data

if __name__ == '__main__':
    eventSource = EventSource(EVENTSOURCE_URL)
    eventSource.onmessage(onmessage, callInThread=True)
    eventSource.start()
    time.sleep(20)
    eventSource.stop()
