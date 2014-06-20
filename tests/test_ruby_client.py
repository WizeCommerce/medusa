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
import os
import unittest
import sys
from thrift_medusa.clients.ruby_client import RubyClient
from thrift_medusa.thrift.thrift_compiler import ThriftCompiler
from thrift_medusa.utils.config import Config
from httpretty import HTTPretty, httprettified


class RubyClientTests(unittest.TestCase):
    def setUp(self):
        self.client = self.__get_client__()
        self.client.initialize()
        self.service_name = os.path.join(os.getcwd(), "../thrift/services/", "wizecommerce.services.example.thrift")

    def __get_client__(self):
        self.config = Config()
        compiler = None
        for item in self.config.get_thrift_option("compilers"):
            compiler = ThriftCompiler(item)
            break

        return RubyClient([], compiler)

    def tearDown(self):
        self.config.reset_configuration()


if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(RubyClientTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
