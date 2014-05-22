import unittest
from lib.utils.naming_helper import *
###---------------------------------------------------------------------------------------------
class CamelConversionTests(unittest.TestCase):

    def test_lower_case_underscore_to_camel_case(self):
        src = "ThisIsATest"
        expected = "this_is_a_test"
        result = camel_case_to_lower_case_underscore(src)
        self.failUnlessEqual(result, expected)

    def test_camel_case_to_lower_case_underscore(self):
        expected = "thisIsATest"
        src = "this_is_a_test"
        result = lower_case_underscore_to_camel_case(src)
        self.failUnlessEqual(result, expected)

    def test_convert(self):
        src = "ThisIsATest"
        expected = "this_is_a_test"
        result = convert(src)
        self.failUnlessEqual(result, expected)
        expected = "thisIsATest"
        src = "this_is_a_test"
        result = convert(src)
        self.failUnlessEqual(result, expected)


    def test_capConvert(self):
        expected = "ThisIsATest"
        src = "this_is_a_test"
        result = cap_convert(src)
        self.failUnlessEqual(result, expected)


if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(CamelConversionTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
