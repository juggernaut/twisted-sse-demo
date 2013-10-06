from twisted.protocols.basic import LineReceiver


class EventSourceProtocol(LineReceiver):
    def __init__(self):
        self.callbacks = {}
        self.finished = None
        # Initialize the event and data buffers
        self.event = 'message'
        self.data = ''

    def setFinishedDeferred(self, d):
        self.finished = d

    def addCallback(self, event, func):
        self.callbacks[event] = func

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
        if self.finished:
            self.finished.callback(None)

    def dispatchEvent(self):
        """
        Dispatch the event
        """
        # If last character is LF, strip it.
        if self.data.endswith('\n'):
            self.data = self.data[:-1]
        if self.event in self.callbacks:
            self.callbacks[self.event](self.data)
        self.data = ''
        self.event = 'message'

def lstrip(value):
    return value[1:] if value.startswith(' ') else value
