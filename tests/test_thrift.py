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
import subprocess
from thrift_medusa.thrift.thrift import Thrift
from thrift_medusa.thrift.thrift_compiler import ThriftCompiler
from mock import MagicMock
import os
import inspect
from thrift_medusa.utils.config import Config


class ThriftTests(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.config.reset_configuration()
        compilers = self.config.get_thrift_option("compilers")
        if compilers is None or len(compilers) == 0:
            self.helper = Thrift(None)
        else:
            thrift_compiler = ThriftCompiler(compilers[0])
            self.helper = Thrift(thrift_compiler)

        project_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), "../")
        project_path = os.path.realpath(project_path)
        self.config.repo_dir = project_path

    def test_extract_string(self):
        raw = \
            """
namespace java com.wizecommerce.service.common

const string VERSION = "0.0.6"

# Type Definitions
typedef i32 Integer

        """
        expected = "0.0.6"

        result = self.helper.__extract_string__("VERSION", raw, "0.0.0")
        self.failUnlessEqual(result, expected)

    # def reset_config(self):
    #     self.config.reset_configuration()
    #     project_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), "../")
    #     project_path = os.path.realpath(project_path)
    #     self.config.repo_dir = project_path


    def test_check_file(self):
        thrift_file = "wizecommerce.services.example.thrift"
        self.helper.check_file(thrift_file)
        #we should reach this point, without any exception thrown.
        thrift_file = "wizecommerce.service.dummyfile.thrift"
        self.assertRaises(IOError,  self.helper.check_file,thrift_file)

    def test_thrift_java_build(self):
        real_methods = {'subprocess': subprocess.call, 'system': os.system, 'chdir': os.chdir,
                        'get_thrift_full_path': self.helper.get_thrift_full_path}
        subprocess.call = MagicMock()
        os.system = MagicMock()
        os.chdir = MagicMock()
        self.helper.get_thrift_full_path = MagicMock()
        thrift_file = "dummy.thrift"
        self.helper.get_thrift_full_path.return_value = thrift_file
        subprocess.call.return_value = 0
        self.helper.thrift_build(thrift_file)
        #########################
        # verify subprocess.call
        #########################
        expected_values = {'compiler': "/usr/local/bin/thrift",
                           'options': "java:private-members,hashcode", 'size': 12,
                           'file': thrift_file}
        call_list = subprocess.call.call_args_list
        self.assertEquals(len(call_list), 1)
        self.verify_subprocess_call(subprocess.call.call_args, expected_values)
        #########################
        # verify chdir calls
        #########################
        call_list = os.chdir.call_args_list
        self.assertEquals(len(call_list), 1)
        call_args = os.chdir.call_args[0][0]
        self.assertEquals(call_args, self.config.work_dir)
        #########################
        # verify system calls
        #########################
        call_list = os.system.call_args_list
        call = call_list[0]
        self.assertEquals(len(call_list), 1)
        parameter = call[0][0]
        self.assertNotEqual(parameter.find("rm -fr"), -1)
        self.assertNotEqual(parameter.find("gen-java"), -1)
        #########################
        # reset all system calls
        #########################
        subprocess.call = real_methods['subprocess']
        os.system = real_methods['system']
        os.chdir = real_methods['chdir']
        self.helper.get_thrift_full_path = real_methods['get_thrift_full_path']


    def test_thrift_ruby_build(self):
        thrift_file = "dummy.thrift"
        real_methods = {'subprocess' : subprocess.call, 'system' : os.system, 'chdir' : os.chdir,
                        'get_thrift_full_path' : self.helper.get_thrift_full_path}
        subprocess.call = MagicMock()
        os.system = MagicMock()
        os.chdir = MagicMock()
        self.helper.get_thrift_full_path = MagicMock()
        self.helper.get_thrift_full_path.return_value = thrift_file
        subprocess.call.return_value = 0
        self.helper.thrift_build(thrift_file=thrift_file, language="ruby")
        #########################
        # verify subprocess.call
        #########################
        expected_values = {'compiler': "/usr/local/bin/thrift",
                           'options': "--gen rb", 'size': 12,
                           'file': thrift_file}
        call_list = subprocess.call.call_args_list
        self.assertEquals(len(call_list), 1)
        self.verify_subprocess_call(subprocess.call.call_args, expected_values)
        #########################
        # verify chdir calls
        #########################
        call_list = os.chdir.call_args_list
        self.assertEquals(len(call_list), 1)
        call_args = os.chdir.call_args[0][0]
        self.assertEquals(call_args, self.config.work_dir)
        #########################
        # verify system calls
        #########################
        call_list = os.system.call_args_list
        call = call_list[0]
        self.assertEquals(len(call_list), 2)
        parameter = call[0][0]
        self.assertNotEqual(parameter.find("rm -fr"), -1)
        self.assertNotEqual(parameter.find("gen-rb"), -1)
        #next call
        call = call_list[1]
        parameter = call[0][0]
        self.assertNotEqual(parameter.find("rm -fr"), -1)
        print parameter
        self.assertNotEqual(parameter.find("work/ruby"), -1)
        #########################
        # reset all system calls
        #########################
        subprocess.call = real_methods['subprocess']
        os.system = real_methods['system']
        os.chdir = real_methods['chdir']
        self.helper.get_thrift_full_path = real_methods['get_thrift_full_path']



    def intercept_thrift_doc_full_path(self, request):
        """
        This method intercepts the call for self.helper.read_full_path and simply returns the
        value passed in.
        """
        return request

    def verify_subprocess_call(self, method_call_args, expected_values):
        call_args = method_call_args[0][0]
        self.assertEquals(len(call_args), expected_values['size'])
        parameter = " ".join(call_args)
        #verify compiler
        self.assertNotEqual(parameter.find(expected_values['compiler']), -1)
        #verify file name
        self.assertNotEqual(parameter.find(expected_values['file']), -1)
        #verify language/options
        self.assertNotEqual(parameter.find(expected_values['options']), -1)
        #verify includes
        self.assertNotEqual(parameter.format("thrift/services"), -1)
        self.assertNotEqual(parameter.format("business-objects"), -1)


    def test_thrift_doc_build(self):
        thrift_file = "dummy.thrift"
        real_methods = {'subprocess' : subprocess.call, 'system' : os.system,
                        'get_thrift_full_path' : self.helper.get_thrift_full_path,
                        'read_thrift_dependencies_recursively': self.helper.read_thrift_dependencies_recursively }
        dependencies = ['dependency1.thrift', 'dependency2.thrift']
        subprocess.call = MagicMock()
        os.system = MagicMock()
        self.helper.get_thrift_full_path = MagicMock()
        self.helper.get_thrift_full_path.return_value = thrift_file
        self.helper.get_thrift_full_path = self.intercept_thrift_doc_full_path
        subprocess.call.return_value = 0
        self.helper.read_thrift_dependencies_recursively = MagicMock()
        self.helper.read_thrift_dependencies_recursively.return_value = dependencies
        self.helper.thrift_build(thrift_file=thrift_file, language="doc")
         #########################
        # verify subprocess.call
        #########################
        expected_values = {'compiler': "/usr/local/bin/thrift",
                           'options': "--gen html", 'size': 14,
                           'file': thrift_file}
        call_list = subprocess.call.call_args_list
        self.assertEquals(len(call_list), 3)
        count = 0
        for dependency_file in dependencies:
            call = call_list[count]
            expected_values['file'] = dependency_file
            call_list = subprocess.call.call_args_list
            self.verify_subprocess_call(call, expected_values)
            count += 1
        #verify client
        expected_values['file'] = thrift_file
        call = call_list[count]
        self.verify_subprocess_call(call, expected_values)
        #########################
        # verify system calls
        #########################
        call_list = os.system.call_args_list
        call = call_list[0]
        self.assertEquals(len(call_list), 1)
        parameter = call[0][0]
        self.assertNotEqual(parameter.find("rm -fr"), -1)
        self.assertNotEqual(parameter.find("gen-html"), -1)
        #########################
        # reset all system calls
        #########################
        subprocess.call = real_methods['subprocess']
        os.system = real_methods['system']
        self.helper.get_thrift_full_path = real_methods['get_thrift_full_path']
        self.helper.read_thrift_dependencies_recursively = real_methods['read_thrift_dependencies_recursively']

    def test_is_service(self):
        dummy = "foobar.services.thrift"
        result = self.helper.is_service(dummy)
        self.assertTrue(result)
        dummy = "foobar.dummy.thrift"
        result = self.helper.is_service(dummy)
        self.assertFalse(result)

    def test_read_thrift_dependencies(self):
        real_file = "wizecommerce.services.example.thrift"
        dependencies = self.helper.read_thrift_dependencies_recursively(real_file)
        self.assertEquals(len(dependencies), 3)
        all_deps = " ".join(dependencies)
        self.assertNotEqual(all_deps.find("exception.invalid"), -1)
        self.assertNotEqual(all_deps.find("enum.example_change"), -1)
        self.assertNotEqual(all_deps.find("bizobj.example"), -1)



    ##TODO: possible enhancement, mock out the file we're reading.
    def test_read_thrift_properties(self):
        thrift_file = "wizecommerce.services.example.thrift"
        properties = self.helper.read_thrift_properties(thrift_file)
        self.assertEquals('example-client', properties['ARTIFACTID'])
        self.assertEquals('0.0.5', properties['VERSION'])
        self.assertEquals('com.wizecommerce.data', properties['GROUPID'])
        print properties


    def test_thrift_compiler(self):
        init = {}
        init['name'] = 'testThrift'
        init['bin'] = '/dev/null'
        init['options'] = 'testoptions'
        init['supported_languages'] = ['java', 'ruby', 'python']
        t = ThriftCompiler(init)
        self.failUnless('testThrift' == t.name)
        self.failUnless('/dev/null' == t.bin)
        self.failUnless('testoptions' == t.options)
        self.failUnless(len(t.languages) == 3)
        self.failUnless(t.is_language_supported('ruby'))
        self.failUnless(not t.is_language_supported('erlang') )

    def test_object_name(self):
        th = Thrift(None)
        src = "/home/user/foobar/blah/wizecommerce.bizobj.sellerprogramrecord.thrift"
        result = th.get_object_name(src)
        expected = "sellerprogramrecord-bizobj"
        self.failUnlessEqual(expected, result)

    def test_complex_object_name(self):
        th = Thrift(None)
        src = "/home/user/foobar/blah/wizecommerce.bizobj.search.foobar.sellerprogramrecord.thrift"
        result = th.get_object_name(src)
        expected = "search-foobar-sellerprogramrecord-bizobj"
        self.failUnlessEqual(expected, result)

    def test_special_case_object_name(self):
        th = Thrift(None)
        src = "/home/user/foobar/blah/wizecommerce.services.sellerprogramrecord.thrift"
        result = th.get_object_name(src)
        expected = "sellerprogramrecord-client"
        self.failUnlessEqual(expected, result)


if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(ThriftTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

