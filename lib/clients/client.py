__author__ = 'sfaci'

import os
from lib.utils.config import Config
from lib.utils.status import Status
from lib.utils.thrift import Thrift
from lib.utils.log import Log
import sys


class Client():
    """
        For the most part, the purpose fo this class is to define an API that you can extend
        to implement your own Client for any language that isn't already supported.
    """
    def get_sandbox(self):
        return self.sandbox

    def set_sandbox(self, value):
        self.sandbox = value


    def __init__(self, services, thriftCompiler):
        self.compiler = thriftCompiler
        self.config = Config()
        self.status = Status()
        self.thrift_helper = Thrift()
        self.log = Log(log_file="status.log", logger_name="status").log
        self.services = services

        pass

    def run(self):

        self.initialize()

        for service in self.services:
            self.process_service(service)

        self.finalize()

    def __build_dependency__(self, business_object):
        """
            Recursively build the dependency and return a list of all dependencies found and successfully built.
        """
        raise NotImplemented
        ##if previous error code has been found, aborting.

    def __build_client__(self, service):
        """
            This method is called to build the actual client, in our case that includes
            all of our services.
        """
        raise NotImplementedError

    def deploy_object(self, properties, business_object, postfix=""):
        """
            The purpose of this method is to handle the deployment / install.
            If set to localMode it will call the appropriate method for handling local installs,
            if doing a production deployment it will call the appropriate method

            postfix str:  a string appended to the artifact name used for releasing snapshot for example.
            properties dict:  list of properties used for doing deployment.
            businessObject str: string containing the name of the thrift file.

        """
        ##Local mode will only build snapshots, for now.
        if self.config.is_local():
            return self.__deploy_local_artifact__(properties=properties, thrift_object=business_object, postfix=postfix)
        else:
            return self.__deploy_production_artifact__(properties=properties, thrift_object=business_object, postfix=postfix)
        return 0

    def check_version(self, **kwargs):
        """
            Returns a boolean checking if the artifact exists on the deployment server.
        """
        raise NotImplementedError

    def __deploy_production_artifact__(self, properties, thrift_object, postfix=""):
        """
            Implement a method responsible for deploying your artifact to your production server.
        """
        raise NotImplemented

    def __deploy_local_artifact__(self, properties, thrift_object, postfix=""):
        """
            Implement a method responsible for performing a local install.
        """
        raise NotImplementedError

    def finalize(self):
        """
            This method is called as a last step to either clean , publish or whatever needs to be done.
        """
        raise NotImplementedError

    def initialize(self):
        """
            Optional, used to initialize/construct any environment or file system settings that need
            to be setup that are specific to the client.
        """
        raise NotImplementedError

    def process_service(self, service):
        """
            This method builds the client and all dependencies assuming appropriate
            metadata is contained in the thrift file.
        """

        #Always get a full path in case input is a relative path from a script
        full_path = os.path.abspath(service)

        os.chdir(self.config.work_dir)

        dependencies = self.thrift_helper.read_thrift_dependencies(full_path)

        #Adding the service file as well to the list.
        if len(dependencies) == 0:
            print "No dependencies for %s" % service
        else:
            for dependency in dependencies:
                file = self.thrift_helper.get_thrift_full_path(dependency)
                self.local_assert(self.__build_dependency__(file), "Failed to process dependencies for {service}".format(service=file))

        self.local_assert(self.__build_client__(full_path),  "Failed to build Client for {service}".format(service=str(service)))
        return 0

    def local_assert(self, exit_code, message, prefix="ERROR: "):
        if exit_code != 0:
            self.log(prefix + message)
            sys.exit(exit_code)

