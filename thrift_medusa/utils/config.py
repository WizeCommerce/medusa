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
import inspect

import os
import yaml
import sys

##Singlelton pattern recipe from:
# http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/

class Config():
    """ A python singleton """
    instance = None


    class __impl:
        """ Implementation of the singleton interface """
        __meta_data__ = {}
        __repo_dir__ = os.getcwd()
        __config_dir__ = os.path.join(__repo_dir__, "config")

        def __init__(self, config, config_dir):
            self.config_dir = config_dir

            stream = open(config, 'r')
            self.__meta_data__ = yaml.load(stream)
            if len(self.__meta_data__) <= 0:
                print "Error: could not load configuration yaml file {config}".format(config=config)
                sys.exit(1)
            self.config_file = config


        @property
        def is_java_source(self):
            """
            Boolean whether to package and deploy the java source or not.
            """
            try:
                return self.__meta_data__.get("java").get("include_source")
            except:
                return False

        @is_java_source.setter
        def is_java_source(self, value):
            try:
                self.__meta_data__.get("java")["include_source"] = value
            except:
                pass

        @property
        def is_doc_enabled(self):
            """
            Boolean denoting whether to generate thrift documentation or not.
            """
            try:
                return self.__meta_data__.get("documentation").get("doc_enabled")
            except:
                return False

        @is_doc_enabled.setter
        def is_doc_enabled(self, value):
            try:
                self.__meta_data__.get("documentation")["doc_enabled"] = value
            except:
                pass

        @property
        def doc_server(self):
            try:
                return self.__meta_data__.get("documentation").get("documentation_server")
            except:
                return {}

        @property
        def doc_work(self):
            try:
                return self.__meta_data__.get("documentation").get("documentation_server").get(
                    "local_path")
            except:
                return None

        @property
        def is_snapshot_doc_enabled(self):
            """
            Boolean denoting whether to generate thrift documentation for snapshots or not.
            """
            try:
                return self.__meta_data__.get("documentation").get("doc_snapshot")
            except:
                return False

        @property
        def documentation_snapshot_postfix(self):
            """
            boolean denoting whether to generate doc for snapshot versions or not.
            """
            try:
                return self.__meta_data__.get("documentation").get("doc_snapshot_postfix")
            except:
                pass


        @documentation_snapshot_postfix.setter
        def documentation_snapshot_postfix(self, value):
            try:
                self.__meta_data__.get("documentation")["doc_snapshot_postfix"] = value
            except:
                pass

        @property
        def is_local_doc_enabled(self):
            try:
                return self.__meta_data__.get("documentation").get("doc_local_enabled")
            except:
                return False

        @is_local_doc_enabled.setter
        def is_local_doc_enabled(self, value):
            try:
                self.__meta_data__.get("documentation")["doc_local_enabled"] = value
            except:
                pass

        @is_snapshot_doc_enabled.setter
        def is_snapshot_doc_enabled(self, value):
            try:
                self.__meta_data__.get("documentation")["doc_snapshot"] = value
            except:
                pass

        @property
        def force_deploy(self):
            """
            Boolean that if set to true will overwrite the currently deployed version.
            """
            try:
                return self.__meta_data__.get("global").get("force_deploy")
            except:
                return False

        @force_deploy.setter
        def force_deploy(self, value):
            try:
                self.__meta_data__.get("global")["force_deploy"] = value
            except:
                pass

        @property
        def is_java(self):
            """
            Boolean denoting if java mode is enabled.
            """
            try:
                return self.__meta_data__.get("global").get("languages").get("java")
            except:
                return False

        @is_java.setter
        def is_java(self, value):
            try:
                self.__meta_data__.get("global").get("languages")["java"] = value
            except:
                pass



        @property
        def is_uber(self):
            """
            Boolean denoting if uber jar is enabled.  ie. build a shaded jar with all dependencies pulled in.
            """
            try:
                return self.__meta_data__.get("java").get("uber_jar")

            except:
                return False


        @is_uber.setter
        def is_uber(self, value):
            try:
                self.__meta_data__.get("java")["uber_jar"] = value
            except:
                pass


        @property
        def is_ruby(self):
            """
            Boolean denoting if ruby mode is enabled.
            """
            try:
                return self.__meta_data__.get("global").get("languages").get("ruby")

            except:
                return False

        @is_ruby.setter
        def is_ruby(self, value):
            try:
                self.__meta_data__.get("global").get("languages")["ruby"] = value
            except:
                pass

        def maven_scm(self, type="default"):
            """
                return the scm maven configuration xml to inject into the auto generated pom.xml
            """
            try:
                pomConfig = self.__meta_data__.get("java").get("poms").get(type)
                if "maven_scm" in pomConfig:
                    return pomConfig.get("maven_scm")
                else:
                    return self.__meta_data__.get("java").get("poms").get("default").get("maven_scm")
            except:
                return None

        def set_maven_scm(self, value, type="default"):
            try:
                self.__meta_data__.get("java").get("poms").get(type)["maven_scm"] = value
            except:
                return None


        def maven_java_source(self, type="default"):
            """
                return the maven plugin configuration xml to inject into the auto generated pom.xml in order
                to package the java source along with the compiled code.
            """
            try:
                pom_config = self.__meta_data__.get("java").get("poms").get(type)
                if "maven_java_source" in pom_config:
                    return pom_config.get("maven_java_source")
                else:
                    return self.__meta_data__.get("java").get("poms").get("default").get("maven_java_source")
            except:
                return None

        def maven_deployment(self, type="default"):
            """
                return the maven configuration xml defining destination URLS to inject into the auto generated pom.xml
            """
            try:
                pomConfig = self.__meta_data__.get("java").get("poms").get(type)
                if "maven_deployment" in pomConfig:
                    return pomConfig.get("maven_deployment")
                else:
                    return self.__meta_data__.get("java").get("poms").get("default").get("maven_deployment")
            except:
                return None

        def set_maven_deployment(self, value, type="default"):
            try:
                self.__meta_data__.get("java").get("poms").get(type)["maven_deployment"] = value
            except:
                return None

        def maven_repos(self, type="default"):
            """
                return the maven configuration xml defining additional maven repos to query to be injected into the pom.xml
            """
            try:
                pom_config = self.__meta_data__.get("java").get("poms").get(type)
                if "maven_repos" in pom_config:
                    return pom_config.get("maven_repos")
                else:
                    return self.__meta_data__.get("java").get("poms").get("default").get("maven_repos")
            except:
                return None

        def set_maven_repos(self, value, type="default"):
            try:
                self.__meta_data__.get("java").get("poms").get(type)["maven_repos"] = value
            except:
                return None

        @property
        def maven_deploy_command(self):
            """
              return the maven command to execute when doing a deployment  usually a mvn deploy:deploy
            """
            try:
                return self.__meta_data__.get("java").get("maven_deploy_command")
            except:
                return None


        @maven_deploy_command.setter
        def maven_deploy_command(self, value):
            try:
                self.__meta_data__.get("java")["maven_deploy_command"] = value
            except:
                return

        @property
        def maven_local_deploy(self):
            """
              return the maven command to execute when doing a local build.  Usually is: mvn package or mvn install
            """
            try:
                return self.__meta_data__.get("java").get("maven_local_deploy")
            except:
                return None


        @maven_local_deploy.setter
        def maven_local_deploy(self, value):
            try:
                self.__meta_data__.get("java")["maven_local_deploy"] = value
            except:
                return

        @property
        def maven_dir(self):
            """
              Relative path to work_dir where generated thrift java files should be copied to.
            """
            try:
                return self.__meta_data__.get("java").get("maven_dir")
            except:
                return None


        @maven_dir.setter
        def maven_dir(self, value):
            try:
                self.__meta_data__.get("java")["maven_dir"] = value
            except:
                return

        def is_local(self):
            """
                Boolean denoting whether project is run in local mode to should try to publish artifacts.
            """
            try:
                return self.__meta_data__.get("global").get("local_install")
            except:
                return None

        def set_local(self, value):
            try:
                self.__meta_data__.get("global")["local_install"] = value
            except:
                pass

        @property
        def repo_dir(self):
            """
               Usually set to current working directory
            """
            return self.__repo_dir__

        @repo_dir.setter
        def repo_dir(self, value):
            self.__repo_dir__ = value

        def get_service_override(self):
            """
               Used in local mode to specify which thrift file to build.
            """
            try:
                return self.__meta_data__.get("global").get("service_override")
            except:
                pass

        def set_service_override(self, value):
            try:
                self.__meta_data__.get("global")["service_override"] = value
            except:
                pass

        def set_languages(self, value):
            """
              Sets the modes of operation ie. which languages should be packaged
            """
            try:
                self.__meta_data__.get("global")["languages"] = value
            except:
                return None

        def get_languages(self):
            try:
                return self.__meta_data__.get("global").get("languages")
            except:
                return None

        @property
        def work_dir(self):
            """
                returns path to working Dir or sandbox if you prefer.
            """
            try:
                return os.path.join(self.__repo_dir__, self.__meta_data__.get("global").get("work_dir"))
            except:
                return None

        @work_dir.setter
        def work_dir(self, value):
            try:
                self.__repo_dir__, self.__meta_data__.get("global")["work_dir"] = value
            except:
                pass

        def get_path(self, type="business_object"):
            """
                Return the full path location to type of resource. ie. bizobj vs service
            """
            try:
                return os.path.join(self.__repo_dir__, self.__meta_data__.get("global").get("paths").get(type))
            except:
                return None

        def set_path(self, value, type="business_object"):
            try:
                self.__repo_dir__, self.__meta_data__.get("global").get("paths")[type] = value
            except:
                return None

        def get_pom_name(self, type="default"):
            """
              Return the pom name to use depending on the type of artifact you wish to build.  (ie. uber jar, service, or bizobj)
            """
            try:
                return os.path.join(self.config_dir, self.__meta_data__.get("java").get("poms").get(type).get("file"))
            except:
                return None

        def get_pom(self, type="default"):
            """
              Returns all pom related properties for requested type.
            """
            try:
                return os.path.join(self.work_dir(), self.__meta_data__.get("java").get("poms").get(type))
            except:
                return None

        def set_pom(self, value, type="default"):
            try:
                self.__meta_data__.get("java").get("poms")[type] = value
            except:
                return None

        def get_global_option(self, key):
            """
               Returns the value for the key specified under the 'global' key
            """
            try:
                return self.__meta_data__.get("global").get(key)
            except:
                return None

        def set_global_option(self, key, value):
            try:
                self.__meta_data__.get("global")[key] = value
            except:
                return None

        def get_ruby_path_option(self, key):
            try:
                return os.path.join(self.work_dir, self.__meta_data__.get("ruby").get(key))
            except:
                return None

        def get_ruby_option(self, key, include_path=False):
            """
                Returns the value associated with the requested key for the ruby config
            """
            try:
                if include_path:
                    return os.path.join(self.work_dir, self.__meta_data__.get("ruby").get(key))
                else:
                    return self.__meta_data__.get("ruby").get(key)
            except:
                return None

        def set_ruby_option(self, key, value):
            try:
                self.__meta_data__.get("ruby")[key] = value
            except:
                return None

        def get_java_path_option(self, key):
            try:
                return os.path.join(self.work_dir, self.__meta_data__.get("java").get(key))
            except:
                return None

        def get_java_option(self, key):
            """
                Returns the value associated with the requested key for the java config
            """
            try:
                return self.__meta_data__.get("java").get(key)
            except:
                return None

        def set_java_option(self, key, value):
            try:
                self.__meta_data__.get("java")[key] = value
            except:
                return None

        @property
        def doc_sandbox(self):
            """
                Returns path to location of java sandbox. ie. transient directory for java build
            """
            try:
                return self.__meta_data__.get("documentation").get("sandbox")
            except:
                return None

        @doc_sandbox.setter
        def doc_sandbox(self, value):
            try:
                self.__meta_data__.get("documentation")["sandbox'"] = value
            except:
                return

        @property
        def java_sandbox(self):
            """
                Returns path to location of java sandbox. ie. transient directory for java build
            """
            try:
                return self.__meta_data__.get("java").get("sandbox")
            except:
                return None

        @java_sandbox.setter
        def java_sandbox(self, value):
            try:
                self.__meta_data__.get("java")["sandbox'"] = value
            except:
                return

        def get_thrift_option(self, key):
            """
                Returns the value associated with the requested key for the thrift config
            """
            try:
                return self.__meta_data__.get("thrift").get(key)
            except:
                return None

        def set_thrift_option(self, key, value):
            try:
                self.__meta_data__["thrift"][key] = value
            except:
                return None

        def reset_configuration(self):
            """
                Reloads data from yaml file, disregarding previous in memory changes.
            """
            stream = open(self.config_file, 'r')
            self.__meta_data__ = yaml.load(stream)
            stream.close()

    def __init__(self, config=None):
        project_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), "../../")
        project_path = os.path.realpath(project_path)
        __config_dir__ =os.path.realpath(os.path.join(project_path, "thrift_medusa/config/"))

        if config is None:
            config = os.path.join(__config_dir__, "appConfig.yaml")
        else:
            config = os.path.join(project_path, config)

        if Config.instance is None:
            # Create and remember instance
            Config.instance = Config.__impl(config, __config_dir__)

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Config.instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.instance, attr, value)
        ###---------------------------------------------------------------------------------------------


