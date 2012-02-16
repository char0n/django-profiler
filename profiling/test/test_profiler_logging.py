import profiling
import unittest
import time

from profiling.test import TestLoggingHandler, log


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
        if profiling.connection is not None:
            profiling.connection = None
        if profiling.settings is not None:
            profiling.settings = None

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


if __name__ == '__main__':
    unittest.main()