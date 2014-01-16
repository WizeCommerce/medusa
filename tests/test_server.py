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
from tests.helper_tools import HelperTools
from thrift_medusa.models.server import Server
from random import randint

__author__ = 'sfaci'



class TestServer(unittest.TestCase):
    server = ""
    def setUp(self):
       raw = {'host': 'localhost', 'user': 'tux', 'password': '123', 'local_path': '/tmp', 'remote_path': 'foobar'}
       self.server = Server(**raw)

    def test_host(self):
        self.setUp()
        self.failUnlessEqual(self.server.host, 'localhost')
        expected = HelperTools.get_random()
        self.server.host = expected
        self.assertEquals(self.server.host, expected)

    def test_user(self):
        self.setUp()
        self.failUnlessEqual(self.server.user, 'tux')
        expected = HelperTools.get_random()
        self.server.user = expected
        self.assertEquals(self.server.user, expected)


    def test_password(self):
        self.setUp()
        self.failUnlessEqual(self.server.password, '123')
        expected = HelperTools.get_random()
        self.server.password = expected
        self.assertEquals(self.server.password, expected)

    def test_local_path(self):
        self.setUp()
        self.failUnlessEqual(self.server.local_path, '/tmp')
        expected = HelperTools.get_random()
        self.server.local_path = expected
        self.assertEquals(self.server.local_path, expected)

    def test_remote_path(self):
        self.setUp()
        self.failUnlessEqual(self.server.remote_path, 'foobar')
        expected = HelperTools.get_random()
        self.server.remote_path = expected
        self.assertEquals(self.server.remote_path, expected)
