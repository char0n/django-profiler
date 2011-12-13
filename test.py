import unittest
from profiling.test import test_profile_decorator, test_profilehook_decorator, test_profiler_logging, test_profiler

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(test_profile_decorator))
    suite.addTests(loader.loadTestsFromModule(test_profilehook_decorator))
    suite.addTests(loader.loadTestsFromModule(test_profiler_logging))
    suite.addTests(loader.loadTestsFromModule(test_profiler))
    unittest.TextTestRunner(verbosity=2).run(suite)