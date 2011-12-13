import logging
import profiling

class TestLoggingHandler(logging.Handler):
    """Logging handler for unittests; keeps log events in internal container."""

    def __init__(self, level=logging.NOTSET):
        """Initializing log events container."""
        logging.Handler.__init__(self, level)
        self.logEvents = []

    def emit(self, record):
        """Inserting new logging record to events container."""
        try:
            self.logEvents.append(record)
        except:
            self.handleError(record)

    def get_log_events(self):
        """Getting shallow copy of log events container."""
        return self.logEvents[:]


log = logging.getLogger(profiling.__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())