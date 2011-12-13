import unittest
from profiling.test import profile_decorator_test, profilehook_decorator_test, profiler_logging_test, profiler_test

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(profile_decorator_test))
    suite.addTests(loader.loadTestsFromModule(profilehook_decorator_test))
    suite.addTests(loader.loadTestsFromModule(profiler_logging_test))
    suite.addTests(loader.loadTestsFromModule(profiler_test))
    unittest.TextTestRunner(verbosity=2).run(suite)