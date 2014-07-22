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
__author__ = 'sfaci'

import sys
import urllib2
import subprocess
import shlex
from lxml import etree

from jinja2 import Template

from thrift_medusa.clients.client import Client
from thrift_medusa.utils.wize_utils import *

#TODO: mock urllib2 library, rather then connecting to an actual http server.
class JavaClient(Client):
    def initialize(self):
        self.sandbox = os.path.join(self.config.work_dir, "%s/java" % self.compiler.name)
        self.sandbox_work = os.path.join(self.config.work_dir, "%s/java_work" % self.compiler.name)
        wize_mkdir(self.sandbox)
        wize_mkdir(self.sandbox_work)

    def __build_dependency__(self, business_object):
        """
            Recursively build the dependency and return a list of all dependencies found and successfully built.
        """
        self.thrift_helper.check_file(business_object)
        self.thrift_helper.__setup_maven__(self.sandbox_work)

        properties = self.thrift_helper.read_thrift_properties(business_object)
        business_dependencies = self.thrift_helper.read_thrift_dependencies(business_object)
        if business_dependencies is not None and len(business_dependencies) > 0:
            for dependency in business_dependencies:
                self.__build_dependency__(dependency)

        properties["MAVEN"] = self.__generate_dependency_xml__(business_dependencies)

        return self.deploy_object(properties, business_object)

    def __build_client__(self, service):
        """
            Builds the service object
        """
        service = self.thrift_helper.get_thrift_full_path(service)
        properties = self.thrift_helper.read_thrift_properties(service)
        os.chdir(self.sandbox_work)
        self.thrift_helper.__setup_maven__(self.sandbox_work)  #cleanup

        service_dependencies = self.thrift_helper.read_thrift_dependencies(service)

        properties["MAVEN"] = self.__generate_dependency_xml__(service_dependencies)
        properties["MAVEN_FILE"] = 'service'
        self.process_maven(properties)

        self.local_assert(self.deploy_object(properties, service),
                          "Failed to deployObject {service} with properties: {properties}".
                          format(service=service, properties=properties))
        return 0

    def process_maven(self, properties):
        """
            injects data into the pom.xml file and builds the artifacts
        """

        if properties.has_key('MAVEN_FILE'):
            type = properties.get('MAVEN_FILE')
            file = open(self.config.get_pom_name(type=type))
        else:
            type = 'default'
            file = open(self.config.get_pom_name(), 'r')

        raw = file.read()
        file.close()

        template = Template(raw)
        if self.config.is_java_source:
            java_source = self.config.maven_java_source(type)
        else:
            java_source = ""

        raw = template.render(WIZESCM=self.config.maven_scm(type), WIZEDEPLOYMENT=self.config.maven_deployment(type),
                              WIZEREPOS=self.config.maven_repos(type),
                              WIZEGROUPID=properties.get("GROUPID"),
                              WIZEID=properties.get("ARTIFACTID") + self.compiler.postfix,
                              WIZEVERSION=properties.get("VERSION"),
                              WIZENAME=properties.get("ARTIFACTID"), WIZEADDITIONALDEPS=properties.get("MAVEN"),
                              WIZEJAVASRC=java_source,
                              THRIFT_VERSION=self.compiler.version)

        raw = raw.replace("WIZEID", properties.get("ARTIFACTID"))


        #Write Pom.xml
        file = open(os.path.join(self.sandbox_work, "pom.xml"), 'w')
        file.write(raw)
        file.close()

    @staticmethod
    def generate_artifact_name(**kwargs):
        """
            returns a concatenation of artifact and version using our java default
            delimter (ie.  "-"
        """
        return kwargs['artifactId'] + "-" + str(kwargs['version']) + ".jar"

    def __do_local_install__(self, businessObject):
        """
            Used for Devel Testing
        """
        os.system("cp target/*.jar %s" % (self.config.localInstall))
        os.system("cp pom.xml %s/%s.xml" % (self.config.localInstall, businessObject))

    def __deploy_local_artifact__(self, properties, thrift_object, postfix=""):
        """
            Will build thrift files, call maven install and copy the resulting
            artifacts to local sandbox
        """
        properties["VERSION"] = increment_version(properties.get("VERSION")) + "-SNAPSHOT"

        #Ensure artifact has not already been built.
        if self.status.is_deployed(properties.get("ARTIFACTID"), properties.get("VERSION"),
                                   "java", self.compiler.name):
            self.log(
                "%s-%s has already been deployed, skipping" % (
                    properties.get("ARTIFACTID"), properties.get("VERSION")))
        else:
            self.thrift_helper.thrift_build(thrift_file=thrift_object, sandbox=self.sandbox_work)
            os.chdir(self.sandbox_work)

            cmd = "rsync -aqP {src}/ {dest}/".format(src=self.config.java_sandbox, dest=self.config.maven_dir)
            self.local_assert(os.system(cmd), "Failed to execute {cmd}".format(cmd=cmd))

            if self.thrift_helper.is_service(thrift_object):
                properties['MAVEN_FILE'] = 'service'
            else:
                properties['MAVEN_FILE'] = 'business_object'

            properties["MAVEN"] = self.__generate_dependency_xml__(
                self.thrift_helper.read_thrift_dependencies(thrift_object),
                True)
            self.process_maven(properties)

            cmd = shlex.split(self.config.maven_local_deploy)

            exit_code = subprocess.call(cmd)
            if exit_code is not 0:
                sys.exit(exit_code)
            else:
                self.status.add_artifact(properties.get("ARTIFACTID"), properties.get("VERSION"),
                                         "java", self.compiler.name)
            os.system("cp target/*.jar %s" % self.sandbox)
            os.system("cp pom.xml %s/%s%s.xml" % (self.sandbox, properties.get("ARTIFACTID"), postfix))
        return 0


    def __deploy_production_artifact__(self, properties, thrift_object, postfix=""):
        """
            Same as deploy local but will also publish the snapshot version of the artifact to remote server and perform
            a release if the version has been incremented.
        """
        check_value = self.check_version(groupId=properties.get("GROUPID"), artifactId=properties.get("ARTIFACTID"),
                                         version=properties.get("VERSION"))

        if self.thrift_helper.is_service(thrift_object):
            check_value_shaded = self.check_shaded_version(groupId=properties.get("GROUPID"),
                                                       artifactId=properties.get("ARTIFACTID"),
                                                       version=properties.get("VERSION"))
        else:
            check_value_shaded = False

        snapshot_check = properties.get("VERSION").find("SNAPSHOT") > -1
        version_check = properties.get("VERSION") != self.config.get_global_option("special_version")
        ## if version hasn't been upload and it's not a special version OR it's a snapshot.. then deploy
	if (check_value and version_check) or snapshot_check  or self.config.force_deploy:
            self.log("%s is okay, proceeding building and deploying version:%s" % (
                properties.get("ARTIFACTID"), properties.get("VERSION")))

            if self.status.is_deployed(properties.get("ARTIFACTID"), properties.get("VERSION"),
                                       "java", self.compiler.name):
                self.log("%s-%s has already been deployed, skipping" % (
                    properties.get("ARTIFACTID"), properties.get("VERSION")))
            else:
                self.thrift_helper.thrift_build(thrift_file=thrift_object, sandbox=self.sandbox_work)
                os.chdir(self.sandbox_work)

                cmd = "rsync -aqP {src}/ {dest}/".format(src=self.config.java_sandbox, dest=self.config.maven_dir)
                self.local_assert(os.system(cmd), "Failed to execute {cmd}".format(cmd=cmd))

                if self.thrift_helper.is_service(thrift_object):
                    properties['MAVEN_FILE'] = 'service'
                else:
                    properties['MAVEN_FILE'] = 'business_object'

                self.process_maven(properties)

                ###Normal Deploy
                exit_code = subprocess.call(shlex.split(self.config.maven_deploy_command))
                self.local_assert(exit_code, "Failed to build %s" % properties.get("ARTIFACTID"))
                self.status.add_artifact(properties.get("ARTIFACTID"), properties.get("VERSION"),
                                         "java", self.compiler.name)

        ##Deploy shaded artifact.
        # This is a secondary check that allows for uber jars to be deployed irrelevant of the status of the normal releases.
        if ((check_value_shaded and version_check) or snapshot_check or self.config.force_deploy) and (
                self.config.is_uber and self.thrift_helper.is_service(thrift_object)):
            #copy uber jar
            uber_properties = properties.copy()
            uber_properties['MAVEN_FILE'] = 'shaded'
            self.process_maven(uber_properties)
            ## Build thrift dependencies in case normal release didn't do so.
            self.thrift_helper.thrift_build(thrift_file=thrift_object, sandbox=self.sandbox_work)
            os.chdir(self.sandbox_work)
            cmd = "rsync -aqP {src}/ {dest}/".format(src=self.config.java_sandbox, dest=self.config.maven_dir)
            self.local_assert(os.system(cmd), "Failed to execute {cmd}".format(cmd=cmd))

            ###Normal Deploy
            exit_code = subprocess.call(shlex.split(self.config.maven_deploy_command))
            if exit_code is not 0:
                self.log("WARN:  failed to publish shaded jar file for {service}".format(
                    service=properties.get("ARTIFACTID")))
            else:
                self.log("Succesfully deployed shaded artifact for {service} version: {version}".format(
                    service=properties.get("ARTIFACTID"), version=properties.get("VERSION")))

        ##build snapshot
        if properties.get("VERSION").find("SNAPSHOT") == -1:
            service_dependencies = self.thrift_helper.read_thrift_dependencies(thrift_object)
            if self.thrift_helper.is_service(thrift_object):
                properties['MAVEN_FILE'] = 'service'
            else:
                properties['MAVEN_FILE'] = 'business_object'

            properties["MAVEN"] = self.__generate_dependency_xml__(service_dependencies, is_snapshot=True)
            ##update pom.xml
            self.process_maven(properties)

            properties["VERSION"] = increment_version(properties.get("VERSION")) + "-SNAPSHOT"
            return self.deploy_object(properties, thrift_object)
        return 0

    def check_shaded_version(self, **kwargs):
        """
            Will connect to the remote server and check if the jar already exists on the remote server
            True:  Will not deploy
            False: Will deploy
        """
        if self.config.is_local():
            return True

        if kwargs is None or len(kwargs) == 0:
            self.log("No arguments received")
            return False
        else:
            if not kwargs.has_key("groupId") or not kwargs.has_key("artifactId") or not kwargs.has_key("version"):
                self.log("missing arguments, Please check your logic thrift file configuration for %s" % kwargs)
                return
            properties = kwargs

        if properties['groupId'] is None or properties['artifactId'] is None or properties['version'] is None:
            return False

        properties['groupId'] = properties.get('groupId').replace(".", "/")

        postfix = self.config.get_java_option("uber_jar_postfix")
        url = self.config.get_java_option("java_host_all") + properties['groupId'] + "/" + properties['artifactId'] + \
              postfix + "/" + \
              str(properties['version']) + "/" + \
              self.generate_artifact_name(groupId=properties['groupId'], artifactId=properties['artifactId'] + postfix,
                                          version=properties['version'])
        self.log("checking if shaded artifacts exists at url: {url}".format(url=url))

        try:
            ret = urllib2.urlopen(url)
            boolean_check = True
            if ret.code == 200:
                boolean_check = False
            else:
                self.log("%s doesn't exists" % url)

            ret.close()
            return boolean_check
        except (urllib2.HTTPError, urllib2.URLError) as e:
            self.log("%s doesn't exists" % url)
            return True

    def check_version(self, **kwargs):
        """
            Will connect to the remote server and check if the jar already exists on the remote server
            True:  Will not deploy
            False: Will deploy
        """
        if self.config.is_local():
            return True

        if kwargs is None or len(kwargs) == 0:
            self.log("No arguments received")
            return False
        else:
            if not kwargs.has_key("groupId") or not kwargs.has_key("artifactId") or not kwargs.has_key("version"):
                self.log("missing arguments, Please check your logic thrift file configuration for %s" % kwargs)
                return
            properties = kwargs

        if properties['groupId'] is None or properties['artifactId'] is None or properties['version'] is None:
            return False

        properties['groupId'] = properties.get('groupId').replace(".", "/")

        url = self.config.get_java_option("java_host") + properties['groupId'] + "/" + properties['artifactId'] + \
              self.compiler.postfix + "/" + str(properties['version']) + "/" + \
              self.generate_artifact_name(groupId=properties['groupId'],
              artifactId=properties['artifactId'] + self.compiler.postfix,
                                          version=properties['version'])

        try:
            ret = urllib2.urlopen(url)
            boolean_check = True

            if ret.code == 200:
                boolean_check = False
            else:
                self.log("%s doesn't exists" % url)

            ret.close()
            return boolean_check
        except (urllib2.HTTPError, urllib2.URLError) as e:
            self.log("%s doesn't exists" % url)
            return True

    def __generate_dependency_xml__(self, deps, is_snapshot=False):
        """
            Reads thrift config and generates XML to be injected into the XML
        """

        if deps is None:
            return ""

        root = etree.Element('dependencies')

        for item in deps:
            properties = self.thrift_helper.read_thrift_properties(item)
            entry = etree.Element("dependency")

            artifact_id = etree.Element("artifactId")
            artifact_id.text = properties.get("ARTIFACTID") + self.compiler.postfix
            entry.append(artifact_id)

            group_id = etree.Element("groupId")
            group_id.text = properties.get("GROUPID")
            entry.append(group_id)

            version = etree.Element("version")
            if is_snapshot:
                version.text = increment_version(properties.get("VERSION")) + "-SNAPSHOT"
            else:
                version.text = properties.get("VERSION")
            entry.append(version)
            root.append(entry)

        raw_xml = etree.tostring(root, pretty_print=True)
        raw_xml = raw_xml.replace("</dependencies>", "").replace("<dependencies>", "")
        if len(deps) == 0:
            return ""
        return raw_xml

    def finalize(self):
        pass
