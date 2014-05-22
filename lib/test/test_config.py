#!/usr/bin/env python
from lib.utils.config import *
import unittest


class ConfigTests(unittest.TestCase):
    def test_object_name(self):
        config1 = Config()
        config2 = Config()
        config1.__setattr__("work_dir", "mooooooo")
        config1.__setattr__("work_dir", "booooo")
        self.failUnlessEqual(config1.work_dir, config2.work_dir)

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

    def test_maven_dir(self):
        config = Config()
        expected = "src/main/java"
        self.failUnless(config.maven_dir.find(expected) >= 0)

    def test_maven_commands(self):
        config = Config()
        prod_command = config.maven_deploy_command
        self.failUnless(prod_command.find("deploy") != -1)
        local_command = config.maven_local_deploy
        print local_command
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
        expected = "thrift/business-objects"
        expected2 = "thrift/services"
        self.failUnless(expected, config.get_path(type="business_object"))
        self.failUnless(expected2, config.get_path(type="service_object"))

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

    def test_ruby_options(self):
        config = Config()
        result = config.get_ruby_option(key="host")
        self.failUnless(result.find("rubygems") > -1)
        result = config.get_ruby_option(key="ssh_host")
        self.failUnless(result.find("rubygems") > -1)
        result = config.get_ruby_option(key="ssh_user")
        self.failUnlessEqual(result, "kato")
        result = config.get_ruby_option(key="ssh_path")
        self.failUnless(result.find("~") > -1)

    def test_java_host(self):
        config = Config()
        result = config.get_java_option("java_host")
        print result
        self.failUnless(result.find("crepo") > -1)

    def test_documentation_config(self):
        config = Config()
        result = config.is_doc_enabled
        expected = True
        self.failUnlessEqual(result, expected)
        result = config.is_snapshot_doc_enabled
        self.failUnlessEqual(result, expected)
        result = config.is_local_doc_enabled
        expected = False
        self.failUnlessEqual(result, expected)

if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

