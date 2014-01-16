"""
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import unittest
from thrift_medusa.utils.naming_helper import *
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
