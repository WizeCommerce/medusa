#!/usr/bin/env python
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
import subprocess
import argparse

from thrift_medusa.utils.wize_utils import *
from thrift_medusa.utils.config import Config
from thrift_medusa.thrift.thrift_compiler import ThriftCompiler
from thrift_medusa.clients.java_client import JavaClient
from thrift_medusa.clients.ruby_client import RubyClient
from thrift_medusa.clients.documentation_client import Documentation

from thrift_medusa.utils.log import Log
from multiprocessing import Process


class PublishClient():
    """
      The purpose of this class is to setup the environment for processing various service objects
    """

    def __init__(self):
        self.client_list = []
        self.remove_structure("logs")
        wize_mkdir("logs")
        self.business_objects = []
        self.service_objects = []
        self.config = Config()
        self.log = Log(log_file=os.path.join(self.config.repo_dir, "logs/status.log"),
                       logger_name="definitions").get_logger()

    def remove_structure(self, dir):
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
        self.remove_structure(self.config.work_dir)
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
            if self.config.is_java and item.is_language_supported("java"):
                self.client_list.append(JavaClient(thrift_objects, item))
            if self.config.is_ruby and item.is_language_supported("ruby"):
                self.client_list.append(RubyClient(thrift_objects, item))
            if self.config.is_doc_enabled and item.is_language_supported("doc"):
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
    """
    Will display the list of all current supported compilers defined in configuration.
    """
    config = Config()
    compilers = config.get_thrift_option("compilers")
    for item in compilers:
        print("found compiler %s with binary at: %s which supports: %s languages" % (item.get('name'), item.get('bin'),
                                                                                     ', '.join(map(str, item.get(
                                                                                         'supported_languages')))))
    sys.exit(0)


def set_compiler(override_compiler):
    """
    Allows user to explicitly use a particular compiler when building thrift artifacts.
    """
    config = Config()
    compilers = config.get_thrift_option("compilers")
    found = False
    compiler = None
    for item in compilers:
        if item['name'] == override_compiler:
            found = True
            compiler = item

    if not found:
        print("compiler {compiler} was not found in yaml configuration".format(compiler=override_compiler))
        sys.exit(1)

    config.set_thrift_option("compilers", [compiler])


def main():
    parser = argparse.ArgumentParser(description='Client Generation Script')
    parser.add_argument('--local', action="store_true", dest="local", default=False, help="Enables Local Mode")
    parser.add_argument('--profile', action="store_true", dest="profile", default=False, help="Profiles App")
    parser.add_argument("--docOnly", action="store_true", dest="doc_only", default=False)
    parser.add_argument('--ruby', action="store_true", dest="ruby", default=False,
                        help="Enables RubyMode, default is Ruby + Java (Local Mode Only)")
    parser.add_argument('--java', action="store_true", dest="java", default=False,
                        help="Enables JavaMode, default is Ruby + Java  (Local Mode Only) ")
    parser.add_argument('--thrift-file', action="store", dest="thrift_file", type=str,
                        help="Override list of services, and use the one specified (Local Mode Only)")
    parser.add_argument('--config', action="store", dest="config", type=str,
                        help="Override default config file and specify your own yaml config")
    parser.add_argument('--compilers', action="store_true", dest="compilers", default=False,
                        help="will list all supported compilers. (Not fully supported)")
    parser.add_argument('--set-compiler', action="store", dest="compiler", type=str,
                        help="accepts a valid compiler name defined in the yaml config.")



    args = parser.parse_args()
    if args.config is None:
        config = Config()
    else:
        config = Config(args.config)

    config.set_local(args.local)
    config.set_service_override(args.thrift_file)

    if args.thrift_file is not None:
        config.set_local(True)

    if args.compilers:
        display_compilers()

    if args.compiler is not None:
        set_compiler(args.compiler)

    publish_client = PublishClient()

    ## these options can only be used in conjunction with local mode
    if config.is_local():
        if args.ruby and args.java:
            print "WARNING: you really should use rubyOverride or JavaOverride, " \
                  "if you pass both it can will fall back on default behavior.  (ie. omit both of them)"
        elif args.ruby:
            config.set_languages({"ruby": True})
        elif args.java:
            config.set_languages({"java": True})

    if args.doc_only:
        config.set_languages({})
        config.is_doc_enabled = True

    if args.profile:
        import cProfile

        cProfile.run('profileProject()')
    else:
        # Create Repo Structure
        publish_client.create_structure()
        # Loop through all of our services check for updates
        publish_client.process_thrift_services()


def profile_project():
    publish_client = PublishClient()
    publish_client.create_structure()
    publish_client.process_thrift_services()


if __name__ == "__main__":
    main()
