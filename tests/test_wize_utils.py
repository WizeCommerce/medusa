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
from helper_tools import HelperTools
from thrift_medusa.utils.wize_utils import *
import unittest


class NewTests(unittest.TestCase):
    def testIncrementVersion(self):
        version = "0.1.5.9"
        result = increment_version(version)
        expected = "0.1.5.10"
        self.failUnlessEqual(expected, result)
        version = "5"
        result = increment_version(version)
        self.assertEquals(result, "6")
        version = "badInput"
        result = increment_version(version)
        self.assertEquals(result, -1)
        version = "0.1.2.3.Bad"
        result = increment_version(version)
        self.assertEquals(result, "-1")

    def test_wize_mkdir(self):
        #folder should already exist.
        tmp_file = tempfile.NamedTemporaryFile(delete=False).name
        self.assertRaises(OSError, wize_mkdir, tmp_file)
        items = HelperTools.get_random_list()
        items.insert(0, "/tmp/")

        some_value = os.path.join(*items)
        wize_mkdir(os.path.join("/tmp/", some_value))


if __name__ == "__main__":
# Run unit tests
    unittest.main()
