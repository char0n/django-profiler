import functools
import sys
import profiling
import unittest
import time
from StringIO import StringIO

from profiling.test import TestLoggingHandler, log


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
        if profiling.connection is not None:
            profiling.connection = None

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

    def test_decorator_stats(self):
        @profiling.profile(stats=True)
        def testing_decorated_function():
            return True
        testing_decorated_function()
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')
        self.assertRegexpMatches(log.handlers[0].get_log_events()[1].getMessage(), r'\d+ function calls in [0-9\.]+ seconds')

    def test_decorator_stats_to_file_like_object(self):
        file_like_object = StringIO()
        @profiling.profile(stats=True, stats_buffer=file_like_object)
        def testing_decorated_function():
            return True
        testing_decorated_function()
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')
        self.assertRegexpMatches(file_like_object.getvalue(), r'\d+ function calls in [0-9\.]+ seconds')
        file_like_object.close()

    def test_decorator_on_decorated_function(self):
        class memoized(object):
           """Decorator that caches a function's return value each time it is called.
           If called later with the same arguments, the cached value is returned, and
           not re-evaluated.
           """
           def __init__(self, func):
              self.func = func
              self.cache = {}
           def __call__(self, *args):
              try:
                 return self.cache[args]
              except KeyError:
                 value = self.func(*args)
                 self.cache[args] = value
                 return value
              except TypeError:
                 # uncachable -- for instance, passing a list as an argument.
                 # Better to not cache than to blow up entirely.
                 return self.func(*args)
           def __repr__(self):
              """Return the function's docstring."""
              return self.func.__doc__
           def __get__(self, obj, objtype):
              """Support instance methods."""
              return functools.partial(self.__call__, obj)

        @memoized
        @profiling.profile
        def testing_decorated_function(arg1, arg2):
            return arg1 + arg2
        self.assertEqual(testing_decorated_function(1, 2), 3)
        self.assertEqual(testing_decorated_function(1, 2), 3)
        self.assertEqual(len(log.handlers[0].get_log_events()), 1)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^testing_decorated_function took: [0-9\.]+ ms$')

    def test_decorator_on_decorator(self):
        class memoized(object):
           """Decorator that caches a function's return value each time it is called.
           If called later with the same arguments, the cached value is returned, and
           not re-evaluated.
           """
           def __init__(self, func):
              self.func = func
              self.cache = {}
           def __call__(self, *args):
              try:
                 return self.cache[args]
              except KeyError:
                 value = self.func(*args)
                 self.cache[args] = value
                 return value
              except TypeError:
                 # uncachable -- for instance, passing a list as an argument.
                 # Better to not cache than to blow up entirely.
                 return self.func(*args)
           def __repr__(self):
              """Return the function's docstring."""
              return self.func.__doc__
           def __get__(self, obj, objtype):
              """Support instance methods."""
              return functools.partial(self.__call__, obj)

        @profiling.profile()
        @memoized
        def testing_decorated_function(arg1, arg2):
            return arg1 + arg2
        self.assertEqual(testing_decorated_function(1, 2), 3)
        self.assertEqual(testing_decorated_function(1, 2), 3)
        self.assertEqual(len(log.handlers[0].get_log_events()), 2)
        self.assertRegexpMatches(log.handlers[0].get_log_events()[0].getMessage(), r'^memoized took: [0-9\.]+ ms$')


if __name__ == '__main__':
    unittest.main()