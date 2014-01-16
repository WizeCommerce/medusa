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
from tests.helper_tools import HelperTools
from thrift_medusa.utils.config import Config
from thrift_medusa.thrift.thrift_compiler import ThriftCompiler


class ThriftCompilerTest(unittest2.TestCase):

    def setUp(self):
        self.yaml = {}
        self.yaml['name'] = 'thrift'
        self.yaml['bin'] = '/bin/'
        self.yaml['options'] = 'SuperOption'
        self.yaml['supported_languages'] =  ['a','b','c']
        self.yaml['compiler_postfix'] = 'postfix'
        self.yaml['version'] = '1.2.3.4'
        self.compiler = ThriftCompiler(self.yaml)

    def test_version(self):
        expected = self.yaml['version']
        self.assertEquals(expected, self.compiler.version)
        expected = HelperTools.get_random()
        self.compiler.version = expected
        self.assertEquals(expected, self.compiler.version)

    def test_bin(self):
        expected = self.yaml['bin']
        self.assertEquals(expected, self.compiler.bin)
        expected = HelperTools.get_random()
        self.compiler.bin = expected
        self.assertEquals(expected, self.compiler.bin)


    def test_name(self):
        expected = self.yaml['name']
        self.assertEquals(expected, self.compiler.name)
        expected = HelperTools.get_random()
        self.compiler.name = expected
        self.assertEquals(expected, self.compiler.name)

    def test_options(self):
        expected = self.yaml['options']
        self.assertEquals(expected, self.compiler.options)
        expected = HelperTools.get_random()
        self.compiler.options = expected
        self.assertEquals(expected, self.compiler.options)

    def test_compiler_postfix(self):
        expected = self.yaml['compiler_postfix']
        self.assertEquals(expected, self.compiler.postfix)
        expected = HelperTools.get_random()
        self.compiler.postfix = expected
        self.assertEquals(expected, self.compiler.postfix)

    def test_supported_languages(self):
        expected = self.yaml['supported_languages']
        self.assertEquals(expected, self.compiler.languages)
        expected = HelperTools.get_random()
        self.compiler.languages = expected
        self.assertEquals(expected, self.compiler.languages)
        self.assertTrue(self.compiler.is_language_supported(expected[0]))
        self.assertFalse(self.compiler.is_language_supported("zzzzzzzz"))

    def test_bad_init_data(self):
        dict = {}
        conf = Config()
        bad_compiler = ThriftCompiler(dict)
        self.assertEquals(bad_compiler.version, "0.6.1")
        self.assertEquals(bad_compiler.postfix, "")
        language = "java"
        self.assertEquals(bad_compiler.is_language_supported("java"), False)
        self.assertEquals(bad_compiler.language_options(), conf.get_thrift_option("global_compiler_options")[language] )

if __name__ == '__main__':
    unittest2.main()
