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
from thrift_medusa.utils.config import *


class ConfigTests(unittest2.TestCase):
    def test_object_name(self):
        config1 = Config()
        config2 = Config()
        original = config1.work_dir
        self.failUnlessEqual(config1.work_dir, config2.work_dir)
        #reset value
        config1.work_dir = original

    def test_is_java_source(self):
        config = Config()
        self.failUnlessEqual(True, config.is_java_source)
        config.is_java_source = False
        self.failUnlessEqual(False, config.is_java_source)
        config.is_java_source = True
        self.failUnlessEqual(True, config.is_java_source)

    def test_is_java(self):
        config = Config()
        config.is_java = True
        self.failUnlessEqual(True, config.is_java)
        config.is_java = False
        self.failUnlessEqual(False, config.is_java)

    def test_is_ruby(self):
        config = Config()
        config.is_ruby = True
        self.failUnlessEqual(True, config.is_ruby)
        config.is_ruby = False
        self.failUnlessEqual(False, config.is_ruby)

    def test_force_deploy(self):
        config = Config()
        self.assertFalse(config.force_deploy)
        config.force_deploy = True
        self.assertTrue(config.force_deploy)
        config.force_deploy = False

    def test_is_vcs(self):
        config = Config()
        config.reset_configuration()
        oldValue = config.is_vcs
        self.assertTrue(config.is_vcs)
        config.is_vcs = False
        self.assertFalse(config.is_vcs)
        config.force_deploy = oldValue

    def test_get_vcs(self):
        config = Config()
        class_name = "GitVCS"
        ins = config.get_vcs_instance()
        self.assertEquals(class_name, ins.__class__.__name__)


    def test_maven_dir(self):
        config = Config()
        expected = "src/main/java"
        self.failUnless(config.maven_dir.find(expected) >= 0)

    def test_maven_commands(self):
        config = Config()
        prod_command = config.maven_deploy_command
        self.failUnless(prod_command.find("deploy") != -1)
        local_command = config.maven_local_deploy
        self.failUnless(local_command.find("deploy") == -1)
        self.failUnless(local_command.find("install") != -1)

    def test_is_local(self):
        config = Config()
        self.failUnlessEqual(True, config.is_local())

    def test_get_pom(self):
        config = Config()
        self.failUnless(config.get_pom_name("default").find("pom_template") >= 0)
        self.failUnless(config.get_pom_name().find("pom_template") >= 0)

    def test_work_dir(self):
        config = Config()
        self.failUnless(len(config.work_dir) > 0)

    def test_maven_scm(self):
        config = Config()
        self.failUnless(config.maven_scm().find('<scm>') >= 0)

    def test_maven_url(self):
        config = Config()
        config.mavenUrl = "www"
        self.failUnlessEqual(config.mavenUrl, "www")

    def test_maven_source(self):
        config = Config()
        self.failUnless(config.maven_java_source().find('attach-sources') >= 0)

    def test_maven_deployment(self):
        config = Config()
        self.failUnless(config.maven_deployment().find('<distributionManagement>') >= 0)

    def test_maven_repos(self):
        config = Config()
        self.failUnless(config.maven_repos().find('<repositories>') >= 0)

    def test_multiple_pom_support(self):
        config = Config()
        service = config.get_pom_name("service")
        self.failUnless(service.find("service") > 0)
        business_object = config.get_pom_name("business_object")
        self.failUnless(business_object.find("business_object") > 0)

    def test_path(self):
        config = Config()
        expected_biz = "thrift/business-objects"
        expected_service = "thrift/services"
        expected_enum = "thrift/enums"
        expected_exception = "thrift/exceptions"
        self.failUnless(expected_biz, config.get_path(type="business_object"))
        self.failUnless(expected_service, config.get_path(type="service_object"))
        self.failUnless(expected_enum, config.get_path(type="enum_object"))
        self.failUnless(expected_exception, config.get_path(type="exception_object"))

    def test_special_version(self):
        config = Config()
        expected = "0.0.0"
        result = config.get_global_option("special_version")
        self.failUnless(expected, result)

    def test_repo_dir(self):
        config = Config()
        expected = os.getcwd()
        result = config.repo_dir
        self.failUnless(expected, result)
        expected = '/tmp'
        config.repo_dir = expected
        self.failUnless(expected, result)

    def test_ruby_options(self):
        config = Config()
        result = config.get_ruby_option(key="host")
        self.failUnless(result.find("rubygems") > -1)
        result = config.get_ruby_option(key="ssh_server")
        self.failUnless(result['host'].find("rubygems") > -1)
        self.failUnlessEqual(result['user'], "kato")
        self.failUnless(result['remote_path'].find("~") > -1)

    def test_java_host(self):
        config = Config()
        result = config.get_java_option("java_host")
        self.failUnless(result.find("nexus.corp.nextag.com") > -1)
        self.failUnless(result.find("releases") > -1)

    def test_documentation_config(self):
        config = Config()
        result = config.is_doc_enabled
        expected = True
        self.failUnlessEqual(result, expected)
        result = config.is_snapshot_doc_enabled
        self.failUnlessEqual(result, expected)
        result = config.is_local_doc_enabled
        expected = True
        self.failUnlessEqual(result, expected)

    def test_uber_jar_values(self):
        config = Config()
        expected = "-shaded"
        result = config.get_java_option("uber_jar_postfix")
        self.failUnlessEqual(expected, result)

    #Begin Constraint tests
    def test_constraints_enabled(self):
        config = Config()
        expected = False
        result = config.constraints_enabled
        self.failUnlessEqual(expected, result)
        expected = True
        config.constraints_enabled = expected
        result = config.constraints_enabled
        self.failUnlessEqual(expected, result)

    def test_empty_constraint_enabled(self):
        config = Config()
        expected = True
        result = config.empty_constraint_enabled
        self.failUnlessEqual(expected, result)
        expected = False
        config.empty_constraint_enabled = expected
        result = config.empty_constraint_enabled
        self.failUnlessEqual(expected, result)

    def test_visibility_check_enabled_(self):
        config = Config()
        expected = True
        result = config.visibility_check_enabled
        self.failUnlessEqual(expected, result)
        expected = False
        config.visibility_check_enabled = expected
        result = config.visibility_check_enabled
        self.failUnlessEqual(expected, result)

    def test_check_field_ordering_enabled(self):
        config = Config()
        expected = False
        result = config.check_field_ordering_enabled
        self.failUnlessEqual(expected, result)
        expected = True
        config.check_field_ordering_enabled = expected
        result = config.check_field_ordering_enabled
        self.failUnlessEqual(expected, result)

    def test_check_version_increment_enabled(self):
        config = Config()
        expected = False
        result = config.check_version_increment_enabled
        self.failUnlessEqual(expected, result)
        expected = True
        config.check_version_increment_enabled = expected
        result = config.check_version_increment_enabled
        self.failUnlessEqual(expected, result)

    def test_get_thrift_constraint(self):
        config = Config()
        expected = False
        result = config.get_thrift_constraint("use_constraints")
        self.failUnlessEqual(expected, result)
        expected = True
        result = config.get_thrift_constraint("enforce_empty")
        self.failUnlessEqual(expected, result)
        result = config.get_thrift_constraint("visibilty_check")
        self.failUnlessEqual(expected, result)
        expected = False
        result = config.get_thrift_constraint("check_field_ordering")
        self.failUnlessEqual(expected, result)
        result = config.get_thrift_constraint("check_version_increment")
        self.failUnlessEqual(expected, result)

    #end Constraint Tests

if __name__ == "__main__":
    # Run unit tests
    suite = unittest2.TestLoader().loadTestsFromTestCase(ConfigTests)
    unittest2.TextTestRunner(verbosity=2).run(suite)

