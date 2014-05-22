#!/usr/bin/env python
from lib.utils.wize_utils import *
import unittest


class NewTests(unittest.TestCase):
    def testIncrementVersion(self):
        version = "0.1.5.9"
        result = increment_version(version)
        expected = "0.1.5.10"
        self.failUnlessEqual(expected, result)


if __name__ == "__main__":
# Run unit tests
    unittest.main()
