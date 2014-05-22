#!/usr/bin/env python
__author__ = 'sfaci'

import os
import sys
import subprocess
import argparse

from lib.utils.wize_utils import *
from lib.utils.config import Config
from lib.utils.thrift import ThriftCompiler
from lib.clients.java_client import JavaClient
from lib.clients.ruby_client import RubyClient
from lib.clients.documentation_client import Documentation

from lib.utils.log import Log
from multiprocessing import Process


class PublishClient():
    """
      The purpose of this class is to setup the environment for processing various service objects
    """

    def __init__(self):
        self.removeStructure("logs")
        wize_mkdir("logs")
        self.business_objects = []
        self.service_objects = []
        self.config = Config()
        self.log = Log(log_file=os.path.join(self.config.repo_dir, "logs/status.log"), logger_name="definitions").get_logger()

    def removeStructure(self, dir):
        """
            Simple method that deletes a directory
        """
        cmd = ['rm', '-fr', dir]
        self.local_assert(subprocess.call(cmd), "failed to run command: {cmd}".format(cmd=str(cmd)))
        return 0

    def local_assert(self, exit_code, message):
        """
        Defines a cleaner version of an assert that is probably more helpful.
        """
        if exit_code != 0:
            self.log.error(message)
            sys.exit(exit_code)

    def create_structure(self):
        """
            Remove old directory structure and re-copy all the files and dependencies
            from the appropriate repos.
        """
        self.removeStructure(self.config.work_dir)
        os.mkdir(self.config.work_dir)

        self.business_objects = build_file_list(self.config.get_path(type="business_object"), ".thrift")
        self.service_objects = build_file_list(self.config.get_path(type="service_object"), ".thrift")


    def update_client_list(self, thrift_objects, compilers):
        """
          Build a list of all clients for each language and compiler type.

          Note: Multiple thrift compilers not currently supported.
        """
        self.client_list = []
        for item in compilers:
            if self.config.is_java:
                self.client_list.append(JavaClient(thrift_objects, item))
            if self.config.is_ruby:
                self.client_list.append(RubyClient(thrift_objects, item))
            if self.config.is_doc_enabled:
               self.client_list.append(Documentation(thrift_objects, item))

    def process_thrift_services(self):
        """
            This method will iterate through all the service and business object thrift files, and
            deploy the maven artifacts and its dependencies
        """
        compiler_list = []
        for item in self.config.get_thrift_option("compilers"):
            t = ThriftCompiler(item)
            compiler_list.append(t)

        thrift_objects = self.service_objects + self.business_objects

        if self.config.is_local() and self.config.get_service_override() is not None:
            self.service_objects = []
            thrift_objects = [self.config.get_service_override()]

        self.update_client_list(thrift_objects, compiler_list)

        process_list = []

        ##TODO: spawn a new process for each compiler

        for client in self.client_list:
            p = Process(target=client.run)
            p.start()
            process_list.append(p)

        #wait for all threads that have been started to terminate.
        map(lambda proc: proc.join(), process_list)

        # #Check exit codes
        for proc in process_list:
            self.local_assert(proc.exitcode, str(proc))


def display_compilers():
    config = Config()
    compilers = config.get_thrift_option("compilers")
    for item in compilers:
        print("found compiler %s with binary at: %s which supports: %s languages" %(item.get('name'), item.get('bin'),
                                      ', '.join(map(str, item.get('supported_languages')))))
    sys.exit(0)

def update_compiler_list(setCompilerList):
        config = Config()
        currentKeys = []
        currentDict = {}
        currentList = config.get_thrift_option("compilers")
        map(lambda i: currentKeys.append(i.get("name")), currentList)

        for item in currentList:
            currentDict[item.get('name')] = item


        override = setCompilerList.split(",")
        keys = list(set(currentKeys).intersection(set(override)))
        newList = []
        for key in keys:
            newList.append(currentDict.get(key))

        if len(newList) > 0:
            config.set_thrift_option("compilers", newList)
        else:
            print("Failed to set compiler to %s" % setCompilerList)
            sys.exit(1)

        display_compilers()


def main():
    parser = argparse.ArgumentParser(description='Client Generation Script')
    parser.add_argument('--local', action="store_true", dest="local", default=False, help="Enables Local Mode")
    parser.add_argument("--docOnly", action="store_true", dest="doc_only", default=False)
    parser.add_argument('--ruby', action="store_true", dest="ruby", default=False,
                        help="Enables RubyMode, default is Ruby + Java (Local Mode Only)")
    parser.add_argument('--java', action="store_true", dest="java", default=False,
                        help="Enables JavaMode, default is Ruby + Java  (Local Mode Only) ")
    parser.add_argument('--service', action="store", dest="service", type=str,
                        help="Override list of services, and use the one specified (requires full path). (Local Mode Only)")
    parser.add_argument('--config', action="store", dest="config", type=str,
                        help="Override default config file and specify your own yaml config")
    parser.add_argument('--compilers', action="store_true", dest="compilers", default=False,
                        help="will list all supported compilers. (Not fully supported)")
    parser.add_argument('--setcompilers', action="store", dest="setcompilers", type=str,
                        help="list the names of the compilers to use (see output of --compilers")

    args = parser.parse_args()
    if args.config is None:
        config = Config()
    else:
        config = Config(args.config)

    config.set_local(args.local)
    config.set_service_override(args.service)

    if args.compilers:
        display_compilers()

    if args.setcompilers:
        update_compiler_list(args.setcompilers)

     #clean up workspace.
    if config.is_local():
        os.system("rm -fvr %s" % config.localInstall)

    publish_client = PublishClient()

    ## these options can only be used in conjunction with local mode
    if config.is_local():
        os.system("rm -fr {work_dir}".format(work_dir=config.work_dir))
        wize_mkdir(config.work_dir)
        if args.ruby and args.java:
            print "WARNING: you really should use rubyOverride or JavaOverride, " \
                  "if you pass both it can will fall back on default behavior.  (ie. ommit both of them)"
        elif args.ruby:
            config.set_languages({"ruby": True})
        elif args.java:
            config.set_languages({"java": True})

    if args.doc_only:
        config.set_languages({})
        config.is_doc_enabled = True


    # Create Repo Structure
    publish_client.create_structure()
    # # Loop through all of our services check for updates
    publish_client.process_thrift_services()


if __name__ == "__main__":
    main()



