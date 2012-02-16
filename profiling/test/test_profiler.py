import logging
import profiling
import unittest
import time

from profiling.test import log


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
        with self.assertRaises(RuntimeError):
            profiler1 = profiling.Profiler('profiler1')
            profiler1.stop()

    def test_profiler_start_in_constructor(self):
        with self.assertRaises(RuntimeError):
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
        profiling.settings = None
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


if __name__ == '__main__':
    unittest.main()