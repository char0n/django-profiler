
__version__ = '1.1'

import logging
import functools
import inspect
import sys
from time import time
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    import cProfile as profile_module
except ImportError:
    import profile as profile_module

try:
    from django.db import connection
except ImportError:
    connection = None
try:
    from django.conf import settings
except ImportError:
    settings = None


class Profiler(object):
    """
    Util for profiling python code mainly in django projects,
    but can be used also on ordinary python code

    """
    def __init__(self, name, start=False, profile_sql=False):
        """Constructor

        :param name: name of the Profiler instance
        :type name: string
        :param start: whether to start immediately after Profiler instantiation
        :type start: bool
        :param profile_sql: whether to profile sql queries or not
        :type profile_sql: bool
        :returns: Profiler instance
        :rtype: profiling.Profiler

        """
        if settings is not None and hasattr(settings, 'PROFILING_LOGGER_NAME'):
            logger_name = settings.PROFILING_LOGGER_NAME
        else:
            logger_name = __name__
        if name.find(' ') == -1:
            logger_name += '.{0}'.format(name)
        self.log = logging.getLogger(logger_name)
        self.name = name
        self.pre_queries_cnt = 0
        self.profile_sql = profile_sql
        if start:
            self.start()

    def get_duration_seconds(self):
        """Getting duration of profiling in seconds.

        :returns: duration of profiling in seconds
        :rtype: float

        """
        if hasattr(self, 'stop_time'):
            stop_time = self.stop_time
        else:
            stop_time = time()
        delta = stop_time - self.start_time
        return delta

    def get_duration_milliseconds(self):
        """Getting duration of profiling in milliseconds.

        :returns: duration of profiling in milliseconds
        :rtype: float

        """
        return round(self.get_duration_seconds() * 1000, 6)

    def get_duration_microseconds(self):
        """Getting duration of profiling in microseconds.

        :returns: duration of profiling in microseconds
        :rtype: float

        """
        return round(self.get_duration_seconds() * 1000000, 6)

    def start(self):
        """
        Starting profiler mechanism. We strongly recommend not to use this
        method directly, but rather use Profiler as context manager.
        """
        self.start_time = time()
        self.pre_queries_cnt = len(connection.queries) if connection is not None else 0

    def stop(self):
        """
        Stopping profiler mechanism. We strongly recommend not to use this
        method directly, but rather use Profiler as context manager.

        :raises: RuntimeError

        """
        if not hasattr(self, 'start_time'):
            raise RuntimeError('Profiler(%s) was stopped before being started' % self.name)

        self.stop_time = time()
        if connection is not None:
            sql_count = len(connection.queries) - self.pre_queries_cnt
            if sql_count > 0:
                sql_time = sum([float(q['time']) for q in connection.queries[self.pre_queries_cnt:self.pre_queries_cnt + sql_count]])
            else:
                sql_time = 0.0
            self.log.info('%s took: %f ms, executed %s queries in %f seconds', self.name, self.get_duration_milliseconds(),
                                                                               sql_count, sql_time)
            if (connection is not None and settings is not None and hasattr(settings, 'PROFILING_SQL_QUERIES') and
                settings.PROFILING_SQL_QUERIES and sql_count > 0) or self.profile_sql:
                for query in connection.queries[self.pre_queries_cnt:]:
                    self.log.info('(%s) %s', query.get('time'), query.get('sql'))
        else:
            self.log.info('%s took: %f ms', self.name, self.get_duration_milliseconds())

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None and exc_value is not None and traceback is not None:
            self.log.exception('%s: Exception "%s" with value "%s" intercepted while profiling', self.name, exc_type, exc_value)
        self.stop()
        return False


def profile(*fn, **options):
    """Decorator for profiling functions and class methods.

    :param profile_sql: whether to profile sql queries or not
    :type profile_sql: bool
    :param stats: whether to use cProfile or profile module to get execution statistics
    :type stats: bool
    :param stats_buffer: how to display execution statistics, defaultly put into logging
    :type stats_buffer: file-like object with write method
    :returns: wrapped function object
    :rtype: types.FunctionType
    :raises: TypeError, IOError

    """
    profile_sql = options.pop('profile_sql', False)
    stats = options.pop('stats', False)
    stats_buffer = options.pop('stats_buffer', None)
    if options:
        raise TypeError('Unsupported keyword arguments: %s' % ','.join(options.keys()))

    def decorator(func):
        try:
            func.__name__
        except AttributeError:
            # This decorator is on top of another decorator implemented as class
            func.__name__ = func.__class__.__name__
        try:
            functools.update_wrapper(decorator, func)
        except AttributeError:
            pass
        def wrapper(*args, **kwargs):
            try:
                functools.update_wrapper(wrapper, func)
            except AttributeError:
                pass
            if (args and hasattr(args[0], '__class__') and args[0].__class__.__dict__.get(func.__name__) is not None and
               args[0].__class__.__dict__.get(func.__name__).__name__ == func.__name__):
               profiler_name = '%s.%s' % (args[0].__class__.__name__, func.__name__)
            else:
                if hasattr(func, '__name__'):
                    profiler_name = func.__name__
                elif hasattr(func, '__class__'):
                    profiler_name = func.__class__.__name__
                else:
                    profiler_name = 'Profiler'
            if stats:
                prof = profile_module.Profile()
                with Profiler(profiler_name, profile_sql=profile_sql):
                    to_return = prof.runcall(func, *args, **kwargs)
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                prof.print_stats()
                statistics = sys.stdout.getvalue()
                sys.stdout.close()
                sys.stdout = old_stdout
                if stats_buffer is not None:
                    stats_buffer.write(statistics)
                else:
                    logger_name = settings.PROFILING_LOGGER_NAME if settings is not None and hasattr(settings, 'PROFILING_LOGGER_NAME') else __name__
                    logging.getLogger('{0}.{1}'.format(logger_name, profiler_name)).info(statistics)
            else:
                with Profiler(profiler_name, profile_sql=profile_sql):
                    to_return = func(*args, **kwargs)
            return to_return
        try:
            return functools.update_wrapper(wrapper, func)
        except AttributeError:
            return wrapper
    
    if fn and inspect.isfunction(fn[0]):
        # Called with no parameter
        return decorator(fn[0])
    else:
        # Called with a parameter
        return decorator