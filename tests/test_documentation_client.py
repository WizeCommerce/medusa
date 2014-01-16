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
import unittest2
import os
from thrift_medusa.clients.documentation_client import Documentation
from thrift_medusa.thrift.thrift_compiler import ThriftCompiler
from thrift_medusa.utils.config import Config


class DocumentationClientTests(unittest2.TestCase):
    def setUp(self):
        self.dict = {}
        self.client = self.__get_client__()
        # self.client.initialize()
        self.service_name = os.path.join(os.getcwd(), "../thrift/services/", "wizecommerce.services.example.thrift")

    def __get_client__(self):
        self.config = Config()
        self.config.reset_configuration()
        compiler = None
        for item in self.config.get_thrift_option("compilers"):
            compiler = ThriftCompiler(item)
        return Documentation([], compiler)

    def test_dummy(self):
        self.assertEquals(1,1)


if __name__ == "__main__":
    # Run unit tests
    suite = unittest2.TestLoader().loadTestsFromTestCase(DocumentationClientTests)
    unittest2.TextTestRunner(verbosity=2).run(suite)
