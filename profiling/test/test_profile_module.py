import unittest
import profile
import sys
from StringIO import StringIO


class TestProfileModule(unittest.TestCase):

    def setUp(self):
        self.old_stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self.old_stdout

    def test_profile_module(self):
        def test(a, b):
            return a*b
        a, b = (2, 3)
        prof = profile.Profile()
        ret = prof.runcall(test, a, b)
        prof.print_stats()
        self.assertIsInstance(ret, int)
        self.assertEqual(ret, 6)
        self.assertRegexpMatches(sys.stdout.getvalue(), r'3 function calls in [0-9\.]+ seconds')


if __name__ == '__main__':
    unittest.main()