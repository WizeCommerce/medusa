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
__author__ = 'Samir Faci'

from thrift_medusa.utils.wize_utils import *
from thrift_medusa.models.server import Server
from thrift_medusa.clients.client import Client
import shlex
import subprocess
import os


class Documentation(Client):
    def initialize(self):
        """
            Called by parent class
        """
        self.sandbox = os.path.join(self.config.work_dir, self.compiler.name, self.config.doc_work)
        self.sandbox_work = self.sandbox + "_work"
        WizeUtilities.wize_mkdir(self.sandbox)
        WizeUtilities.wize_mkdir(self.sandbox_work)


    def process_service(self, service):
        """
            will attempt to generate documentation for release + dev version depending on
            configuration.
        """
        properties = self.thrift_helper.read_thrift_properties(service)
        self.log("Generating documentation for {thrift_file}".format(thrift_file=service))
        self.thrift_helper.thrift_build(thrift_file=service, language="doc", sandbox=self.sandbox_work)
        self.deploy_object(properties, service)

    def __get_local_path(self, properties, thrift_file):

        prefix = self.__get_prefix(thrift_file)
        destination = os.path.join(self.sandbox, prefix, properties['ARTIFACTID'], properties['VERSION'])
        WizeUtilities.wize_mkdir(destination)
        return destination




    def generate_documentation(self, properties, thrift_file):
        """
        Generic method that generates doc, same procedure for production and local
        """
        destination = self.__get_local_path(properties, thrift_file)
        cmd = "rsync -avP {local}/ {dest}".format(local=os.path.join(self.sandbox_work, self.config.doc_sandbox), dest=destination)
        exit_code = subprocess.call(shlex.split(cmd))
        if exit_code is not 0:
            self.log("Failed to generate documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))
        else:
            self.log("successfully uploaded documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))

        if self.config.is_snapshot_doc_enabled:
            properties = properties.copy()
            properties['VERSION'] = WizeUtilities.increment_version(
                properties.get('VERSION')) + self.config.documentation_snapshot_postfix
            destination = self.__get_local_path(properties, thrift_file)
            cmd = "rsync -avP {local}/ {dest}".format(local=os.path.join(self.sandbox_work, self.config.doc_sandbox), dest=destination)
            exit_code = subprocess.call(shlex.split(cmd))
            if exit_code is not 0:
                self.log("Failed to generate documentation for {artifact} {version}".format(
                    artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))
            else:
                self.log("successfully uploaded documentation for {artifact} {version}".format(
                    artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))

        return 0

    def __deploy_local_artifact__(self, properties, thrift_object, postfix=""):
        if self.config.is_local_doc_enabled:
            self.generate_documentation(properties, thrift_object)
        return 0

    def __deploy_production_artifact__(self, properties, thrift_object, postfix=""):
        """
            Will generate thrift based documentation and will try to publish it either locally or remotely.
        """
        prefix = self.__get_prefix(thrift_object)

        documentation_location=os.path.join(self.sandbox_work, self.config.doc_sandbox)
        server = Server(**self.config.doc_server.copy())
        server.local_path = os.path.join(documentation_location)
        server.remote_path = os.path.join(server.remote_path, prefix, properties['ARTIFACTID'], properties['VERSION'])
        exit_code = self.publish_production_documentation(properties, server)

        if self.config.is_snapshot_doc_enabled:
            properties['VERSION'] = WizeUtilities.increment_version(
                properties.get('VERSION')) + self.config.documentation_snapshot_postfix
            server = Server(**self.config.doc_server.copy())
            server.local_path = os.path.join(documentation_location)
            server.remote_path = os.path.join(server.remote_path, prefix, properties['ARTIFACTID'], properties['VERSION'])
        exit_code = self.publish_production_documentation(properties, server)
        return exit_code



    def publish_production_documentation(self, properties, server):
        """
        Will rsync locally generated doc to remote server.
        """
        WizeUtilities.wize_sshmkdir(**server.dictionary)
        cmd = "rsync -a {local_path}/ {user}@{host}:{remote_path}".format(user=server.user,
                                                                          local_path=server.local_path,
                                                                          host=server.host,
                                                                          remote_path=server.remote_path)
        exit_code = subprocess.call(shlex.split(cmd))
        if exit_code is not 0:
            self.log("Failed to generate documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))
        else:
            self.log("successfully uploaded documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))

        return exit_code

    def publish_local_documentation(self, properties, server):
        """
        Generates and copies documentation to specified path.  If path doesn't exist an attempt will be made to create
        it.
        """
        WizeUtilities.wize_mkdir(server.remote_path)
        cmd = "rsync -a {local_path}/ {remote_path}".format(local_path=server.local_path, remote_path=server.remote_path)
        exit_code = subprocess.call(shlex.split(cmd))
        if exit_code is not 0:
            self.log("Failed to generate documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))
        else:
            self.log("successfully uploaded documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))



    def __get_prefix(self, thrift_object):
       if self.thrift_helper.is_service(thrift_object):
            return "services"
       else:
            return "business-objects"


    def finalize(self):
        """
            Nothing to be done.
        """
        pass
