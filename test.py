import logging
import profiling
import unittest
import time
from StringIO import StringIO
import sys
import types

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
        self.assertIsInstance(profiler.get_duration_seconds(), float)
        self.assertGreaterEqual(profiler.get_duration_seconds(), 0.1)

    def test_get_duration_milliseconds(self):
        with profiling.Profiler('profiler1') as profiler:
            time.sleep(0.1)
        self.assertIsInstance(profiler.get_duration_milliseconds(), float)
        self.assertGreaterEqual(profiler.get_duration_milliseconds(), 0.1 * 1000)

    def test_get_duration_microseconds(self):
        with profiling.Profiler('profiler1') as profiler:
            time.sleep(0.1)
        self.assertIsInstance(profiler.get_duration_microseconds(), float)
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

    def test_logger_name_from_settings(self):
        class Settings(object): pass
        settings = Settings()
        settings.PROFILING_LOGGER_NAME = 'custom_logger_name'
        profiling.settings = settings
        with profiling.Profiler('profiler1') as profiler:
            pass
        self.assertEqual(profiler.log.name,'custom_logger_name.profiler1')
        delattr(profiling, 'settings')
        with profiling.Profiler('profiler1') as profiler:
            pass
        self.assertEqual(profiler.log.name, 'profiling.profiler1')
        log.handlers = []


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

    CONNECTION_CLASS = None

    @classmethod
    def setUpClass(cls):
        class Connection(object): pass
        ProfilerLoggingTest.CONNECTION_CLASS = Connection

    @classmethod
    def tearDownClass(cls):
        ProfilerLoggingTest.CONNECTION_CLASS = None

    def setUp(self):
        self.handler = TestLoggingHandler()
        log.handlers = [self.handler]

    def tearDown(self):
        log.handlers = filter(lambda h: h is self.handler, log.handlers)
        self.handler = None
        if hasattr(profiling, 'connection'):
            del profiling.connection
        if hasattr(profiling, 'settings'):
            del profiling.settings

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

    def test_exception_interception_context(self):
        with self.assertRaises(Exception):
            with profiling.Profiler('profiler1'):
                time.sleep(0.1)
                raise Exception('Intercepting Exception')
                time.sleep(0.1)
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1: Exception "<type \'exceptions.Exception\'>" with value "Intercepting Exception" intercepted while profiling$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'^profiler1 took: [0-9\.]+ ms$')

    def test_exception_interception_no_context(self):
        with self.assertRaises(Exception):
            profiler = profiling.Profiler('profiler1')
            profiler.start()
            time.sleep(0.1)
            raise Exception('Intercepting Exception')
            time.sleep(0.1)
            profiler.stop()
        self.assertEqual(len(log.handlers[0].get_log_events()), 0)

    def test_no_query_execution_context(self):
        with profiling.Profiler('profiler1'):
            pass
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms$')

    def test_no_query_execution_no_context(self):
        profiler = profiling.Profiler('profiler1')
        profiler.start()
        profiler.stop()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms$')

    def test_query_execution_context(self):
        connection = self.CONNECTION_CLASS()
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
        connection = self.CONNECTION_CLASS()
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
        connection = self.CONNECTION_CLASS()
        connection.queries = [
            { 'time': 0.1 },
            { 'time': 0.2 }
        ]
        profiling.connection = connection
        with profiling.Profiler('profiler1'):
            connection = self.CONNECTION_CLASS()
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
        connection = self.CONNECTION_CLASS()
        connection.queries = [
            { 'time': 0.1 },
            { 'time': 0.2 }
        ]
        profiling.connection = connection
        profiler = profiling.Profiler('profiler1')
        profiler.start()
        connection = self.CONNECTION_CLASS()
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

    def test_profiling_sql_queries_setting_constant(self):
        class Settings(object): pass
        settings = Settings()
        settings.PROFILING_SQL_QUERIES = True
        profiling.settings = settings
        connection = self.CONNECTION_CLASS()
        connection.queries = [
            { 'time': 0.1, 'sql': 'SELECT * FROM test_table1' },
            { 'time': 0.2, 'sql': 'SELECT * FROM test_table2' }
        ]
        profiling.connection = connection
        with profiling.Profiler('profiler1'):
            connection = self.CONNECTION_CLASS()
            connection.queries = [
                { 'time': 0.1, 'sql': 'SELECT * FROM test_table1' },
                { 'time': 0.2, 'sql': 'SELECT * FROM test_table2' },
                { 'time': 0.3, 'sql': 'SELECT * FROM test_table3' },
                { 'time': 0.4, 'sql': 'SELECT * FROM test_table4' }
            ]
            profiling.connection = connection
        self.assertEqual(len(log.handlers[0].get_log_events()), 3)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms, executed 2 queries in 0.700000 seconds$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'^\(0\.3\) SELECT \* FROM test_table3$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[2].getMessage(), r'^\(0\.4\) SELECT \* FROM test_table4$')

    def test_not_profiling_sql_queries_setting_constant(self):
        class Settings(object): pass
        settings = Settings()
        settings.PROFILING_SQL_QUERIES = False
        profiling.settings = settings
        connection = self.CONNECTION_CLASS()
        connection.queries = [
            { 'time': 0.1, 'sql': 'SELECT * FROM test_table1' },
            { 'time': 0.2, 'sql': 'SELECT * FROM test_table2' }
        ]
        profiling.connection = connection
        with profiling.Profiler('profiler1'):
            connection = self.CONNECTION_CLASS()
            connection.queries = [
                { 'time': 0.1, 'sql': 'SELECT * FROM test_table1' },
                { 'time': 0.2, 'sql': 'SELECT * FROM test_table2' },
                { 'time': 0.3, 'sql': 'SELECT * FROM test_table3' },
                { 'time': 0.4, 'sql': 'SELECT * FROM test_table4' }
            ]
            profiling.connection = connection
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms, executed 2 queries in 0.700000 seconds$')

    def test_profiling_sql_queries_constructor(self):
        with profiling.Profiler('profiler1', profile_sql=True):
            connection = self.CONNECTION_CLASS()
            connection.queries = [
                { 'time': 0.1, 'sql': 'SELECT * FROM test_table1' },
                { 'time': 0.2, 'sql': 'SELECT * FROM test_table2' }
            ]
            profiling.connection = connection
        self.assertEqual(len(log.handlers[0].get_log_events()), 3)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms, executed 2 queries in 0.300000 seconds$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'^\(0\.1\) SELECT \* FROM test_table1$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[2].getMessage(), r'^\(0\.2\) SELECT \* FROM test_table2$')

    def test_not_profiling_sql_queries_constructor(self):
        with profiling.Profiler('profiler1'):
            connection = self.CONNECTION_CLASS()
            connection.queries = [
                { 'time': 0.1, 'sql': 'SELECT * FROM test_table1' },
                { 'time': 0.2, 'sql': 'SELECT * FROM test_table2' }
            ]
            profiling.connection = connection
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^profiler1 took: [0-9\.]+ ms, executed 2 queries in 0.300000 seconds$')

        
class ProfileDecoratorTest(unittest.TestCase):

    CONNECTION_CLASS = None

    @classmethod
    def setUpClass(cls):
        class Connection(object): pass
        ProfileDecoratorTest.CONNECTION_CLASS = Connection

    @classmethod
    def tearDownClass(cls):
        ProfileDecoratorTest.CONNECTION_CLASS = None

    def setUp(self):
        self.handler = TestLoggingHandler()
        log.handlers = [self.handler]

    def tearDown(self):
        log.handlers = filter(lambda h: h is self.handler, log.handlers)
        self.handler = None
        if hasattr(profiling, 'connection'):
            del profiling.connection

    def test_decorator(self):
        @profiling.profile
        def testing_decorated_function():
            return True
        testing_decorated_function()
        self.assertEqual(testing_decorated_function.__name__, 'testing_decorated_function')
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')

    def test_decorator_param(self):
        @profiling.profile(profile_sql=True)
        def testing_decorated_function():
            return True
        testing_decorated_function()
        self.assertEqual(testing_decorated_function.__name__, 'testing_decorated_function')
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')

    def test_decorator_invalid_param(self):
        with self.assertRaises(TypeError):
            @profiling.profile(invalid_param=True)
            def testing_decorated_function():
                return True

    def test_decorator_query_execution(self):
        @profiling.profile
        def testing_decorated_function():
            connection = self.CONNECTION_CLASS()
            connection.queries = [
                { 'time': 0.1 },
                { 'time': 0.2 }
            ]
            profiling.connection = connection
            return True
        testing_decorated_function()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms, executed 2 queries in 0.300000 seconds$')

    def test_decorator_query_execution_pre_queries(self):
        connection = self.CONNECTION_CLASS()
        connection.queries = [
            { 'time': 0.1 },
            { 'time': 0.2 }
        ]
        profiling.connection = connection
        @profiling.profile
        def testing_decorated_function():
            connection = self.CONNECTION_CLASS()
            connection.queries = [
                { 'time': 0.1 },
                { 'time': 0.2 },
                { 'time': 0.3 },
                { 'time': 0.4 }
            ]
            profiling.connection = connection
            return True
        testing_decorated_function()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms, executed 2 queries in 0.700000 seconds$')

    def test_decorator_exception_interception_in_function(self):
        @profiling.profile
        def testing_decorated_function():
            time.sleep(0.1)
            raise Exception('Exception in decorated function')
            return True
        with self.assertRaises(Exception):
            testing_decorated_function()
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function: Exception "<type \'exceptions.Exception\'>" with value "Exception in decorated function" intercepted while profiling$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')

    def test_decorator_exception_interception_in_method(self):
        class TestingClass(object):
            @profiling.profile
            def testing_decorated_method(self):
                time.sleep(0.1)
                raise Exception('Exception in decorated method')
                return True
        with self.assertRaises(Exception):
            instance = TestingClass()
            instance.testing_decorated_method()
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^TestingClass.testing_decorated_method: Exception "<type \'exceptions.Exception\'>" with value "Exception in decorated method" intercepted while profiling$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'^TestingClass.testing_decorated_method took: [0-9\.]+ ms$')

    def test_decorator_decorating_function(self):
        @profiling.profile
        def testing_decorated_function():
            return True
        testing_decorated_function()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')

    def test_decorator_decorating_class(self):
        class TestingClass(object):
            @profiling.profile
            def testing_decorated_method(self):
                return True
        instance = TestingClass()
        instance.testing_decorated_method()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^TestingClass.testing_decorated_method took: [0-9\.]+ ms$')

    def test_decorator_profile_sql(self):
        @profiling.profile(profile_sql=True)
        def testing_decorated_function():
            connection = self.CONNECTION_CLASS()
            connection.queries = [
                { 'time': 0.1, 'sql': 'SELECT * FROM test_table1' },
                { 'time': 0.2, 'sql': 'SELECT * FROM test_table2' },
            ]
            profiling.connection = connection
            return True
        testing_decorated_function()
        self.assertEqual(len(log.handlers[0].get_log_events()), 3)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms, executed 2 queries in 0.300000 seconds$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'^\(0\.1\) SELECT \* FROM test_table1$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[2].getMessage(), r'^\(0\.2\) SELECT \* FROM test_table2$')
        

if hasattr(profiling, 'profilehook'):
    class ProfilehookDecoratorTest(unittest.TestCase):

        CONNECTION_CLASS = None

        @classmethod
        def setUpClass(cls):
            class Connection(object): pass
            ProfilehookDecoratorTest.CONNECTION_CLASS = Connection

        @classmethod
        def tearDownClass(cls):
            ProfilehookDecoratorTest.CONNECTION_CLASS = None

        def setUp(self):
            self.handler = TestLoggingHandler()
            log.handlers = [self.handler]
            self.old_stdout = sys.stdout
            sys.stdout = StringIO()

        def tearDown(self):
            log.handlers = filter(lambda h: h is self.handler, log.handlers)
            self.handler = None
            if hasattr(profiling, 'connection'):
                del profiling.connection
            sys.stdout.close()
            sys.stdout = self.old_stdout

        def test_decorator(self):
            @profiling.profilehook
            def testing_decorated_function():
                return True
            testing_decorated_function()
            self.assertEqual(len(log.handlers[0].get_log_events()), 1)
            self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')
            self.assertRegexpMatches(sys.stdout.getvalue(), r'\*\*\* PROFILER RESULTS \*\*\*')

        def test_decorator_wrapper(self):
            def testing_decorated_function():
                return True
            result = profiling.profilehook(testing_decorated_function)
            self.assertIsInstance(result, types.FunctionType)


        def test_decorator_query_execution(self):
            @profiling.profilehook
            def testing_decorated_function():
                connection = self.CONNECTION_CLASS()
                connection.queries = [
                    { 'time': 0.1 },
                    { 'time': 0.2 }
                ]
                profiling.connection = connection
                return True
            testing_decorated_function()
            self.assertEqual(len(log.handlers[0].get_log_events()), 1)
            self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms, executed 2 queries in 0.300000 seconds$')
            self.assertRegexpMatches(sys.stdout.getvalue(), r'\*\*\* PROFILER RESULTS \*\*\*')

        def test_decorator_query_execution_pre_queries(self):
            connection = self.CONNECTION_CLASS()
            connection.queries = [
                { 'time': 0.1 },
                { 'time': 0.2 }
            ]
            profiling.connection = connection
            @profiling.profilehook
            def testing_decorated_function():
                connection = self.CONNECTION_CLASS()
                connection.queries = [
                    { 'time': 0.1 },
                    { 'time': 0.2 },
                    { 'time': 0.3 },
                    { 'time': 0.4 }
                ]
                profiling.connection = connection
                return True
            testing_decorated_function()
            self.assertEqual(len(log.handlers[0].get_log_events()), 1)
            self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms, executed 2 queries in 0.700000 seconds$')
            self.assertRegexpMatches(sys.stdout.getvalue(), r'\*\*\* PROFILER RESULTS \*\*\*')

        def test_decorator_exception_interception_in_function(self):
            @profiling.profilehook
            def testing_decorated_function():
                time.sleep(0.1)
                raise Exception('Exception in decorated function')
                return True
            with self.assertRaises(Exception):
                testing_decorated_function()
            self.assertEqual(len(log.handlers[0].get_log_events()), 2)
            self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function: Exception "<type \'exceptions.Exception\'>" with value "Exception in decorated function" intercepted while profiling$')
            self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')
            self.assertRegexpMatches(sys.stdout.getvalue(), r'\*\*\* PROFILER RESULTS \*\*\*')

        def test_decorator_exception_interception_in_method(self):
            class TestingClass(object):
                @profiling.profilehook
                def testing_decorated_method(self):
                    time.sleep(0.1)
                    raise Exception('Exception in decorated method')
                    return True
            with self.assertRaises(Exception):
                instance = TestingClass()
                instance.testing_decorated_method()
            self.assertEqual(len(log.handlers[0].get_log_events()), 2)
            self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^TestingClass.testing_decorated_method: Exception "<type \'exceptions.Exception\'>" with value "Exception in decorated method" intercepted while profiling$')
            self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'^TestingClass.testing_decorated_method took: [0-9\.]+ ms$')
            self.assertRegexpMatches(sys.stdout.getvalue(), r'\*\*\* PROFILER RESULTS \*\*\*')

        def test_decorator_decorating_function(self):
            @profiling.profilehook
            def testing_decorated_function():
                return True
            testing_decorated_function()
            self.assertEqual(len(log.handlers[0].get_log_events()), 1)
            self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')
            self.assertRegexpMatches(sys.stdout.getvalue(), r'\*\*\* PROFILER RESULTS \*\*\*')

        def test_decorator_decorating_class(self):
            class TestingClass(object):
                @profiling.profilehook
                def testing_decorated_method(self):
                    return True
            instance = TestingClass()
            instance.testing_decorated_method()
            self.assertEqual(len(log.handlers[0].get_log_events()), 1)
            self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^TestingClass.testing_decorated_method took: [0-9\.]+ ms$')
            self.assertRegexpMatches(sys.stdout.getvalue(), r'\*\*\* PROFILER RESULTS \*\*\*')


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(ProfilerTest))
    suite.addTest(loader.loadTestsFromTestCase(ProfilerLoggingTest))
    suite.addTest(loader.loadTestsFromTestCase(ProfileDecoratorTest))
    if hasattr(profiling, 'profilehook'):
        suite.addTest(loader.loadTestsFromTestCase(ProfilehookDecoratorTest))
    unittest.TextTestRunner(verbosity=2).run(suite)