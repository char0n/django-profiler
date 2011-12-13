from profiling.test import TestLoggingHandler, log
from StringIO import StringIO
import sys
import types
import profiling
import unittest
import time


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