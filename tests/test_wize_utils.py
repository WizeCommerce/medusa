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
import tempfile
from mock import MagicMock
from helper_tools import HelperTools
from thrift_medusa.utils.wize_utils import WizeUtilities
import unittest2
import os


class WizeUtilsTests(unittest2.TestCase):
    def test_increment_version(self):
        version = "0.1.5.9"
        result = WizeUtilities.increment_version(version)
        expected = "0.1.5.10"
        self.failUnlessEqual(expected, result)
        version = "5"
        result = WizeUtilities.increment_version(version)
        self.assertEquals(result, "6")
        version = "badInput"
        result = WizeUtilities.increment_version(version)
        self.assertEquals(result, -1)
        version = "0.1.2.3.Bad"
        result = WizeUtilities.increment_version(version)
        self.assertEquals(result, "-1")

    def test_wize_mkdir(self):
        ##Save mock objects.
        real_methods = {'mkdir': os.mkdir}
        #folder should already exist.
        os.mkdir = MagicMock()
        ###
        tmp_file = tempfile.NamedTemporaryFile(delete=False).name
        self.assertRaises(OSError, WizeUtilities.wize_mkdir, tmp_file)
        items = HelperTools.get_random_list()
        some_value = os.path.join(*items)
        WizeUtilities.wize_mkdir(os.path.join("/tmp/", some_value))
        ##verify mocked objects
        call_list = os.mkdir.call_args_list
        ## since /tmp exists, we should recursively create the remaining directories
        self.assertEquals(len(call_list), len(items))
        #########################
        # reset all mocked calls.
        #########################
        os.mkdir = real_methods['mkdir']


if __name__ == "__main__":
# Run unit tests
    unittest2.main()
