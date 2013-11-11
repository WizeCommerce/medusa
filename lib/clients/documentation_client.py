from lib.models.server import Server

__author__ = 'sfaci'

from lib.clients.client import Client

import os
import shutil
from lib.utils.wize_utils import *
import shlex, subprocess


class Documentation(Client):
    def initialize(self):
        """
            Called by parent class
        """
        self.sandbox = os.path.join(self.config.work_dir, self.compiler.name, self.config.doc_work)
        self.sandbox_work = self.sandbox + "_work"
        wize_mkdir(self.sandbox)
        wize_mkdir(self.sandbox_work)


    def process_service(self, service):
        """
            will attempt to generate documentation for release + dev version depending on
            configuration.
        """
        properties = self.thrift_helper.read_thrift_properties(service)
        self.deploy_object(properties, service)

    def __get_local_path(self, properties, thrift_file):

        prefix = self.__get_prefix(thrift_file)
        dest = os.path.join(self.sandbox, prefix, properties['ARTIFACTID'], properties['VERSION'])
        wize_mkdir(dest)
        return dest




    def generate_documentation(self, properties, thrift_object):
        """
        Generic method that generates doc, same procedure for production and local
        """
        self.thrift_helper.thrift_build(thrift_file=thrift_object, language="doc", sandbox=self.sandbox_work)
        dest = self.__get_local_path(properties, thrift_object)
        cmd = "rsync -avP {local}/ {dest}".format(local=os.path.join(self.sandbox_work, self.config.doc_sandbox), dest=dest)
        exit_code = subprocess.call(shlex.split(cmd))
        if exit_code is not 0:
            self.log("Failed to generate documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))
        else:
            self.log("successfully uploaded documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))

        #self.document_version(thrift_object, properties)
        if self.config.is_snapshot_doc_enabled:
            properties = properties.copy()
            properties['VERSION'] = increment_version(
                properties.get('VERSION')) + self.config.documentation_snapshot_postfix
            dest = self.__get_local_path(properties, thrift_object)
            cmd = "rsync -avP {local}/ {dest}".format(local=os.path.join(self.sandbox_work, self.config.doc_sandbox), dest=dest)
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
        self.thrift_helper.thrift_build(thrift_file=thrift_object, language="doc", sandbox=self.sandbox_work)
        self.publish_documentation(service=thrift_object, properties=properties,
                                   documentation_location=os.path.join(self.sandbox_work, self.config.doc_sandbox))


    def publish_production_documentation(self, properties, server):
        """
        Will rsync locally generated doc to remote server.
        """
        wize_sshmkdir(**server.dictionary)
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
        wize_mkdir(server.remote_path)
        cmd = "rsync -a {local_path}/ {remote_path}".format(local_path=server.local_path, remote_path=server.remote_path)
        exit_code = subprocess.call(shlex.split(cmd))
        if exit_code is not 0:
            self.log("Failed to generate documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))
        else:
            self.log("successfully uploaded documentation for {artifact} {version}".format(
                artifact=properties.get('ARTIFACTID'), version=properties.get('VERSION')))

        return exit_code


    def __get_prefix(self, thrift_object):
       if self.thrift_helper.is_service(thrift_object):
            return "services"
       else:
            return "business-objects"


    def publish_documentation(self, documentation_location, properties, service):
        """
            Will generate thrift based documentation and will try to publish it either locally or remotely.
        """
        prefix = self.__get_prefix(service)

        server = Server(**self.config.doc_server.copy())
        server.local_path = os.path.join(documentation_location)
        server.remote_path = os.path.join(server.remote_path, prefix, properties['ARTIFACTID'], properties['VERSION'])
        exit_code = self.publish_production_documentation(properties, server)

        if self.config.is_snapshot_doc_enabled:
            properties['VERSION'] = increment_version(
                properties.get('VERSION')) + self.config.documentation_snapshot_postfix
            server = Server(**self.config.doc_server.copy())
            server.local_path = os.path.join(documentation_location)
            server.remote_path = os.path.join(server.remote_path, prefix, properties['ARTIFACTID'], properties['VERSION'])
        exit_code = self.publish_production_documentation(properties, server)
        return exit_code



    def finalize(self):
        """
            Nothing to be done.
        """
        pass
