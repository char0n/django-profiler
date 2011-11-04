import logging
import profiling
import unittest
import time


log = logging.getLogger(profiling.__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())

class ProfilerTest(unittest.TestCase):

    def test_context_execution(self):
        with profiling.Profiler('profiler1'):
            a = 0
            a += 1
        self.assertEqual(a, 1)

    def test_get_duration(self):
        with profiling.Profiler('profiler1') as profiler:
            time.sleep(0.1)
        self.assertGreaterEqual(profiler.get_duration_seconds(), 0.1)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), 0.1 * 1000)
        self.assertGreaterEqual(profiler.get_duration_microseconds(), 0.1 * 1000000)

    def test_get_duration_seconds(self):
        with profiling.Profiler('profiler1') as profiler:
            time.sleep(0.1)
        self.assertGreaterEqual(profiler.get_duration_seconds(), 0.1)

    def test_get_duration_milliseconds(self):
        with profiling.Profiler('profiler1') as profiler:
            time.sleep(0.1)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), 0.1 * 1000)

    def test_get_duration_microseconds(self):
        with profiling.Profiler('profiler1') as profiler:
            time.sleep(0.1)
        self.assertGreaterEqual(profiler.get_duration_microseconds(), 0.1 * 1000000)

    def test_profiler_context(self):
        with profiling.Profiler('profiler1') as profiler:
            time.sleep(0.1)
        self.assertGreaterEqual(profiler.get_duration_seconds(), 0.1)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), 0.1 * 1000)
        self.assertGreaterEqual(profiler.get_duration_microseconds(), 0.1 * 1000000)

    def test_profiler_no_context(self):
        profiler = profiling.Profiler('profiler1')
        profiler.start()
        time.sleep(0.1)
        profiler.stop()
        self.assertGreaterEqual(profiler.get_duration_seconds(), 0.1)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), 0.1 * 1000)
        self.assertGreaterEqual(profiler.get_duration_microseconds(), 0.1 * 1000000)

    def test_profiler_exception_context(self):
        with self.assertRaises(Exception):
            with profiling.Profiler('profiler1') as profiler:
                time.sleep(0.1)
                raise Exception('Testing Exception')
        self.assertGreaterEqual(profiler.get_duration_seconds(), 0.1)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), 0.1 * 1000)
        self.assertGreaterEqual(profiler.get_duration_microseconds(), 0.1 * 1000000)

    def test_profiler_exception_no_context(self):
        with self.assertRaises(Exception):
            profiler = profiling.Profiler('profiler1')
            profiler.start()
            time.sleep(0.1)
            raise Exception('Testing Exception')
            profiler.stop()
        self.assertGreaterEqual(profiler.get_duration_seconds(), 0.1)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), 0.1 * 1000)
        self.assertGreaterEqual(profiler.get_duration_microseconds(), 0.1 * 1000000)

    def test_nested_profilers_context(self):
        with profiling.Profiler('level_1') as profiler1:
            a = 0
            time.sleep(0.1)
            with profiling.Profiler('level_2') as profiler2:
                b = 1
                time.sleep(0.1)
        self.assertEqual(a, 0)
        self.assertEqual(b, 1)
        self.assertGreaterEqual(profiler1.get_duration_seconds(), 0.2)
        self.assertGreaterEqual(profiler1.get_duration_milliseconds(), 0.2 * 1000)
        self.assertGreaterEqual(profiler1.get_duration_microseconds(), 0.2 * 1000000)
        self.assertGreaterEqual(profiler2.get_duration_seconds(), 0.1)
        self.assertGreaterEqual(profiler2.get_duration_milliseconds(), 0.1 * 1000)
        self.assertGreaterEqual(profiler2.get_duration_microseconds(), 0.1 * 1000000)

    def test_nested_profilers_no_context(self):
        profiler1 = profiling.Profiler('level_1')
        profiler1.start()
        a = 0
        time.sleep(0.1)
        profiler2 = profiling.Profiler('level_2')
        profiler2.start()
        b = 1
        time.sleep(0.1)
        profiler2.stop()
        profiler1.stop()

        self.assertEqual(a, 0)
        self.assertEqual(b, 1)
        self.assertGreaterEqual(profiler1.get_duration_seconds(), 0.2)
        self.assertGreaterEqual(profiler1.get_duration_milliseconds(), 0.2 * 1000)
        self.assertGreaterEqual(profiler1.get_duration_microseconds(), 0.2 * 1000000)
        self.assertGreaterEqual(profiler2.get_duration_seconds(), 0.1)
        self.assertGreaterEqual(profiler2.get_duration_milliseconds(), 0.1 * 1000)
        self.assertGreaterEqual(profiler2.get_duration_microseconds(), 0.1 * 1000000)

    def test_profiler_no_start(self):
        with self.assertRaises(Exception):
            profiler1 = profiling.Profiler('profiler1')
            profiler1.stop()

    def test_profiler_start_in_constructor(self):
        with self.assertRaises(Exception):
            profiler1 = profiling.Profiler('profiler1')
            profiler1.stop()
        profiler1 = profiling.Profiler('profiler1', start=True)
        profiler1.stop()

    def test_profiler_stop_after_exception_interception(self):
        with self.assertRaises(Exception):
            with profiling.Profiler('profiler1') as profiler:
                time.sleep(0.1)
                raise Exception('Intercepting exception')
                time.sleep(1)
        self.assertGreaterEqual(profiler.get_duration_seconds(), 0.1)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), 0.1 * 1000)
        self.assertGreaterEqual(profiler.get_duration_microseconds(), 0.1 * 1000000)
        self.assertLess(profiler.get_duration_seconds(), 1)
        self.assertLess(profiler.get_duration_milliseconds(), 1 * 1000)
        self.assertLess(profiler.get_duration_microseconds(), 1 * 1000000)

    def test_duration_before_stop_context(self):
        with profiling.Profiler('profiler1') as profiler:
            duration_before_sec = profiler.get_duration_seconds()
            duration_before_mili = profiler.get_duration_milliseconds()
            duration_before_micro = profiler.get_duration_microseconds()
            time.sleep(0.1)
            duration_before_sec2 = profiler.get_duration_seconds()
            duration_before_mili2 = profiler.get_duration_milliseconds()
            duration_before_micro2 = profiler.get_duration_microseconds()
        self.assertGreaterEqual(duration_before_sec, 0)
        self.assertGreaterEqual(duration_before_mili, 0)
        self.assertGreaterEqual(duration_before_micro, 0)
        self.assertGreaterEqual(duration_before_sec2, 0.1)
        self.assertGreaterEqual(duration_before_mili2, 0.1)
        self.assertGreaterEqual(duration_before_micro2, 0.1)
        self.assertGreaterEqual(profiler.get_duration_seconds(), duration_before_sec)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), duration_before_mili)
        self.assertGreaterEqual(profiler.get_duration_microseconds(), duration_before_micro)
        

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


class ProfilerLoggingTest(unittest.TestCase):

    def setUp(self):
        self.handler = TestLoggingHandler()
        log.handlers = [self.handler]

    def tearDown(self):
        log.handlers = filter(lambda h: h is self.handler, log.handlers)
        self.handler = None

    def test_logging_context(self):
        with profiling.Profiler('profiler1'):
            pass
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)

    def test_multiple_logging_context(self):
        with profiling.Profiler('profiler1'):
            pass
        with profiling.Profiler('profiler2'):
            pass
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)

    def test_nested_logging_context(self):
        with profiling.Profiler('profiler1'):
            with profiling.Profiler('profiler2'):
                pass
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)

    def test_logging_no_context(self):
        profiler1 = profiling.Profiler('profiler1')
        profiler1.start()
        profiler1.stop()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)

    def test_multiple_logging_no_context(self):
        profiler1= profiling.Profiler('profiler1')
        profiler1.start()
        profiler1.stop()
        profiler2 = profiling.Profiler('profiler2')
        profiler2.start()
        profiler2.stop()
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)

    def test_nested_logging_no_context(self):
        profiler1= profiling.Profiler('profiler1')
        profiler1.start()
        profiler2 = profiling.Profiler('profiler2')
        profiler2.start()
        profiler2.stop()
        profiler1.stop()
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)

    def test_sublogger_context(self):
        with profiling.Profiler('sublogger'):
            pass
        self.assertEqual(log.handlers[0].get_log_events()[0].name, '%s.%s' % (profiling.__name__, 'sublogger'))

    def test_no_sublogger_context(self):
        with profiling.Profiler('testing sublogger'):
            pass
        self.assertEqual(log.handlers[0].get_log_events()[0].name, profiling.__name__)

    def test_class_sublogger_context(self):
        with profiling.Profiler('Class.method'):
            pass
        self.assertEqual(log.handlers[0].get_log_events()[0].name, '%s.%s' % (profiling.__name__, 'Class.method'))

    def test_sublogger_no_context(self):
        profiler = profiling.Profiler('sublogger')
        profiler.start()
        profiler.stop()
        self.assertEqual(log.handlers[0].get_log_events()[0].name, '%s.%s' % (profiling.__name__, 'sublogger'))

    def test_no_sublogger_no_context(self):
        profiler = profiling.Profiler('testing sublogger')
        profiler.start()
        profiler.stop()
        self.assertEqual(log.handlers[0].get_log_events()[0].name, profiling.__name__)

    def test_class_sublogger_no_context(self):
        profiler = profiling.Profiler('Class.method')
        profiler.start()
        profiler.stop()
        self.assertEqual(log.handlers[0].get_log_events()[0].name, '%s.%s' % (profiling.__name__, 'Class.method'))

    def test_no_query_execution_context(self):
        with profiling.Profiler('profiler1'):
            pass
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms$')

    def test_no_1query_execution_no_context(self):
        profiler = profiling.Profiler('profiler1')
        profiler.start()
        profiler.stop()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms$')

    def test_query_execution_context(self):
        class Connection(object): pass
        connection = Connection()
        connection.queries = []
        profiling.connection = connection
        with profiling.Profiler('profiler1'):
            connection.queries = [
                { 'time': 0.1 },
                { 'time': 0.2 }
            ]
            profiling.connection = connection

        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms, executed 2 queries in 0.300000 seconds$')

    def test_query_execution_no_context(self):
        class Connection(object): pass
        connection = Connection()
        connection.queries = []
        profiling.connection = connection
        profiler = profiling.Profiler('profiler1')
        profiler.start()
        connection.queries = [
            { 'time': 0.1 },
            { 'time': 0.2 }
        ]
        profiling.connection = connection
        profiler.stop()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms, executed 2 queries in 0.300000 seconds$')

    def test_query_execution_pre_queries_context(self):
        class Connection(object): pass
        connection = Connection()
        connection.queries = [
            { 'time': 0.1 },
            { 'time': 0.2 }
        ]
        profiling.connection = connection
        with profiling.Profiler('profiler1'):
            connection = Connection()
            connection.queries = [
                { 'time': 0.1 },
                { 'time': 0.2 },
                { 'time': 0.3 },
                { 'time': 0.4 }
            ]
            profiling.connection = connection
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms, executed 2 queries in 0.700000 seconds$')

    def test_query_execution_pre_queries_no_context(self):
        class Connection(object): pass
        connection = Connection()
        connection.queries = [
            { 'time': 0.1 },
            { 'time': 0.2 }
        ]
        profiling.connection = connection
        profiler = profiling.Profiler('profiler1')
        profiler.start()
        connection = Connection()
        connection.queries = [
            { 'time': 0.1 },
            { 'time': 0.2 },
            { 'time': 0.3 },
            { 'time': 0.4 }
        ]
        profiling.connection = connection
        profiler.stop()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms, executed 2 queries in 0.700000 seconds$')

class DecoratorTest(unittest.TestCase):

    def test_decorator_no_params(self):
        @profiling.profile
        def testing_decorated_function():
            return True
        testing_decorated_function()
        testing_decorated_function()
        testing_decorated_function()
        testing_decorated_function()
        testing_decorated_function()
        testing_decorated_function()
        testing_decorated_function()
        testing_decorated_function()

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(ProfilerTest))
    suite.addTest(loader.loadTestsFromTestCase(ProfilerLoggingTest))
    suite.addTest(loader.loadTestsFromTestCase(DecoratorTest))
    unittest.TextTestRunner(verbosity=2).run(suite)