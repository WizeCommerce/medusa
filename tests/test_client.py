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
from thrift_medusa.clients.client import Client
from thrift_medusa.thrift.thrift_compiler import ThriftCompiler
from thrift_medusa.utils.config import Config


class BaseClientTests(unittest2.TestCase):
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
        return Client([], compiler)

    def test_not_implemented_methods(self):
        client = self.__get_client__()
        self.assertRaises(NotImplementedError,  client.__build_dependency__,"DummyFile")
        self.assertRaises(NotImplementedError, client.__build_client__, "service")
        self.assertRaises(NotImplementedError, client.check_version, **self.dict)
        self.assertRaises(NotImplementedError, client.__deploy_production_artifact__, self.dict, "boo")
        self.assertRaises(NotImplementedError, client.__deploy_local_artifact__, self.dict, "boo")
        self.assertRaises(NotImplementedError, client.finalize)
        self.assertRaises(NotImplementedError, client.initialize)

    def test_deploy_object(self):
        client = self.__get_client__()
        self.config.set_local(True)
        self.assertRaisesRegexp(NotImplementedError, ".*Deploy Local Artifact.*", client.deploy_object, self.dict, "dummy")
        self.config.set_local(False)
        self.assertRaisesRegexp(NotImplementedError, ".*Deploy Production Artifact.*", client.deploy_object, self.dict, "dummy")

    def test_sandbox(self):
        client = self.__get_client__()
        client.set_sandbox("DummySandbox")
        self.assertEquals("DummySandbox", client.get_sandbox())

if __name__ == "__main__":
    # Run unit tests
    suite = unittest2.TestLoader().loadTestsFromTestCase(BaseClientTests)
    unittest2.TextTestRunner(verbosity=2).run(suite)
