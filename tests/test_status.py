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
from thrift_medusa.utils.status import Status

class StatusTests(unittest.TestCase):
    def test_object_name(self):
        status1 = Status()
        status2 = Status()
        status1.add_artifact("foobar", "0.1.0")
        status1.add_artifact("moo", "0.2.0")
        self.failUnless(status2.is_deployed("foobar", "0.1.0"))
        self.failUnless(status2.is_deployed("moo", "0.2.0"))

    def test_is_deployed(self):
        status = Status()
        name = "foobar"
        version = "1.0"
        status.add_artifact(name, version)
        self.assertTrue(status.is_deployed(name, version))

if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(StatusTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
