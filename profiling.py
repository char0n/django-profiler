import logging
from time import time
from profilehooks import profile as hook_profile
try:
    from django.db import connection
except Exception:
    pass


class Profiler(object):

    def __init__(self, name, start=False):
        logger_name = __name__
        if name.find(' ') == -1:
            logger_name += '.%s' % name
        self.log = logging.getLogger(logger_name)
        self.name = name
        self.pre_queries_cnt = 0
        if start:
            self.start()

    def get_duration_seconds(self):
        if hasattr(self, 'stop_time'):
            stop_time = self.stop_time
        else:
            stop_time = time()
        delta = stop_time - self.start_time
        return delta

    def get_duration_milliseconds(self):
        return round(self.get_duration_seconds() * 1000, 6)

    def get_duration_microseconds(self):
        return round(self.get_duration_seconds() * 1000000, 6)

    def start(self):
        self.start_time = time()
        self.pre_queries_cnt = len(connection.queries) if globals().has_key('connection') else 0

    def stop(self):
        """
        If Exception is intercepted, profiler will end prematurely and counts the
        time only to the point of Exception raising


        """
        if not hasattr(self, 'start_time'):
            raise Exception('Profiler(%s) was stopped before being started' % self.name)

        self.stop_time = time()
        if globals().has_key('connection'):
            sql_count = len(connection.queries) - self.pre_queries_cnt
            if sql_count > 0:
                sql_time = sum([float(q['time']) for q in connection.queries[self.pre_queries_cnt:self.pre_queries_cnt + sql_count]])
            else:
                sql_time = 0.0
            self.log.info('%s took: %f ms, executed %s queries in %f seconds',
                self.name, self.get_duration_milliseconds(),
                sql_count, sql_time
            )
        else:
            self.log.info('%s took: %f ms', self.name, self.get_duration_milliseconds())

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        if exc_type is not None and exc_value is not None and traceback is not None:
            self.log.exception('%s: Exception "%s" with value "%s" intercepted while profiling', self.name, exc_type, exc_value)
        return False


def profilehook(func):
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            if args and hasattr(args[0], '__class__') and args[0].__class__.__dict__.get(func.__name__) is not None \
                and args[0].__class__.__dict__.get(func.__name__).__name__ == func.__name__:
                profiler_name = '%s.%s' % (args[0].__class__.__name__, func.__name__)
            else:
                profiler_name = func.__name__
            with Profiler(profiler_name):
                to_return = func(*args, **kwargs)
            return to_return
        inner_wrapper.__doc__ = func.__doc__
        inner_wrapper.__name__ = func.__name__
        inner_wrapper.__dict__ = func.__dict__
        inner_wrapper.__module__ = func.__module__
        return inner_wrapper

    w = wrapper(hook_profile(fn=func, immediate=False))
    w.__doc__ = func.__doc__
    w.__name__ = func.__name__
    w.__dict__ = func.__dict__
    w.__module__ = func.__module__
    return w


def profile(func):
    def wrapper(*args, **kwargs):
        if args and hasattr(args[0], '__class__') and args[0].__class__.__dict__.get(func.__name__) is not None \
            and args[0].__class__.__dict__.get(func.__name__).__name__ == func.__name__:
            profiler_name = '%s.%s' % (args[0].__class__.__name__, func.__name__)
        else:
            profiler_name = func.__name__
        with Profiler(profiler_name):
            to_return = func(*args, **kwargs)
        return to_return
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__module__ = func.__module__
    return wrapper