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
from thrift_medusa.clients.java_client import JavaClient
from thrift_medusa.thrift.thrift_compiler import ThriftCompiler
from thrift_medusa.utils.config import Config
from httpretty import HTTPretty, httprettified
from minimock import mock

class JavaClientTests(unittest.TestCase):

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

        return JavaClient([], compiler)

    @httprettified
    def test_check_version_pretty(self):
        self.config.set_local(False)
        expected = False
        expected_url = 'http://nexus.corp.nextag.com:8081/content/repositories/releases/com/wizecommerce/data/tag-client/0.0.13/tag-client-0.0.13.jar'
        HTTPretty.register_uri(HTTPretty.GET, expected_url, body="Hello")
        check_value = self.client.check_version(groupId='com.wizecommerce.data', artifactId='tag-client',
                                         version='0.0.13')
        self.failUnlessEqual(check_value, expected)
        check_value = self.client.check_version(groupId='com.wizecommerce.data', artifactId='tag-client',
                                           version='X.Y.ZZ')
        expected = True
        self.failUnlessEqual(check_value, expected)


    @httprettified
    def test_check_shaded_version_pretty(self):
        self.config.set_local(False)
        expected = False
        expected_url = 'http://crepo.corp.nextag.com/repo/components/com/wizecommerce/data/tag-client-shaded/0.0.13/tag-client-shaded-0.0.13.jar'
        HTTPretty.register_uri(HTTPretty.GET, expected_url, body="Hello")
        check_value_shaded = self.client.check_shaded_version(groupId='com.wizecommerce.data', artifactId='tag-client',
                                         version='0.0.13')
	print check_value_shaded
	print expected
        assert check_value_shaded == expected
        self.failUnlessEqual(check_value_shaded, expected)

        check_value_shaded = self.client.check_shaded_version(groupId='com.wizecommerce.data', artifactId='tag-client',
                                         version='X.Y.ZZ')
        expected = True
        assert check_value_shaded == expected

    def tearDown(self):
        self.config.reset_configuration()

if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(JavaClientTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
