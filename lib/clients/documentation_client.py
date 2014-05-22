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
        wize_mkdir(self.sandbox)


    def document_version(self, service, properties):
        """
           Generate thrift documentation for each thrift file, determine the dependencies, and call
           the appropriate method to upload the results.

        """
        work = os.path.join(self.sandbox, properties.get("ARTIFACTID"), properties.get("VERSION"))
        deps = os.path.join(work, "deps")
        os.chdir(self.config.work_dir)
        os.system("rm -fr %s" % self.sandbox)
        wize_mkdir(deps)
        os.chdir(work)

        full_path = self.thrift_helper.get_thrift_full_path(service)
        dependencies = self.thrift_helper.read_thrift_dependencies_recursively(full_path)

        if len(dependencies) is not 0:
            for item in dependencies:
                file = self.thrift_helper.get_thrift_full_path(item)
                shutil.copy(file, deps)
            dependencies = "-I " + deps
        else:
            dependencies = ""

        cmd = "thrift {dependencies} -r --gen html {service}".format(service=full_path, dependencies=dependencies)
        self.local_assert(os.system(cmd), "Failed to execute {cmd}".format(cmd=cmd))
        self.publish_documentation(work, properties, service)

    def process_service(self, service):
        """
            will attempt to generate documentation for release + dev version depending on
            configuration.
        """
        properties = self.thrift_helper.read_thrift_properties(service)
        self.deploy_object(properties, service)

    def generate_documentation(self, properties, thrift_object):
        """
        Generic method that generates doc, same procedure for production and local
        """
        self.document_version(thrift_object, properties)
        if self.config.is_snapshot_doc_enabled:
            properties['VERSION'] = increment_version(
                properties.get('VERSION')) + self.config.documentation_snapshot_postfix
            self.document_version(thrift_object, properties)
        return 0

    def __deploy_local_artifact__(self, properties, thrift_object, postfix=""):
        if self.config.is_local_doc_enabled:
            return self.generate_documentation(properties, thrift_object)
        return 0

    def __deploy_production_artifact__(self, properties, thrift_object, postfix=""):
        return self.generate_documentation(properties, thrift_object)


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

    def publish_documentation(self, documentation_location, properties, service):
        """
            Will generate thrift based documentation and will try to publish it either locally or remotely.
        """
        if self.thrift_helper.is_service(service):
            prefix = "services"
        else:
            prefix = "business-objects"

        server = Server(**self.config.doc_server.copy())
        server.local_path = os.path.join(documentation_location, 'gen-html')
        server.remote_path = os.path.join(server.remote_path, prefix, properties['ARTIFACTID'], properties['VERSION'])

        if self.config.is_local() and self.config.is_local_doc_enabled:
            #doc_local_enabled
            return self.publish_local_documentation(properties, server)
        else:
            return self.publish_production_documentation(properties, server)

    def finalize(self):
        """
            Nothing to be done.
        """
        pass
