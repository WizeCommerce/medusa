__author__ = 'sfaci'

import os
import subprocess
from lib.utils.log import Log
from lib.utils.config import Config
from lib.utils.wize_utils import *
import shlex
import re
import sys


class Thrift():
    def __init__(self):
        self.config = Config()
        self.log = Log(log_file="status.log", logger_name="status").log
        # defines the language compiler to spawn.
        self.build = {"ruby": self.__thrift_ruby_build__, "java": self.__thrift_java_build__}

    def __setup_maven__(self):
        """
            removes the old maven structure, and recreates it
        """
        os.system("rm -fr %s" % (os.path.join(self.config.work_dir, "src")))
        os.system("rm -f %s" % os.path.join(self.config.work_dir, "pom.xml"))
        wize_mkdir(self.config.maven_dir)
        wize_mkdir(self.config.get_thrift_option("thrift"))

    def check_file(self, thrift_file):
        """
            checks whether a file exists or not in the workdir
        """
        thrift_file = self.get_thrift_full_path(thrift_file)

        if not os.path.exists(thrift_file):
            self.log("Error, file {prettyfile} does not exist".format(prettyfile=thrift_file))
            sys.exit(1)


    def __thrift_java_build__(self, thrift_file):
        """
        compile the thrift file passed in to java format.
        :param thrift_file:
        """
        thrift_file = self.get_thrift_full_path(thrift_file)
        os.system("rm -fr %s" % self.config.java_sandbox)
        os.chdir(self.config.work_dir)
        self.log("Building java class for %s" % thrift_file)
        cmd = "thrift -I {business_objects} -I {services} --gen java:private-members  {file}".format(
            business_objects=self.config.get_path(type="business_object"), services=self.config.get_path(type="service_object"),
            file=thrift_file)
        exit_code = subprocess.call(shlex.split(cmd))
        if not exit_code == 0:
            self.log("failed to compile thrift file {file}".format(file=thrift_file))
            sys.exit(1)

    def __thrift_ruby_build__(self, thrift_file):
        """
        compile the thrift file passed in to ruby format.
        :param thrift_file:
        """
        thrift_file = self.get_thrift_full_path(thrift_file)
        os.system("rm -fr %s" % (self.config.get_ruby_option("sandbox", True)))
        os.system("rm -fr %s" % (os.path.join(self.config.work_dir, "ruby")))
        cmd = "thrift -I %s -I %s --gen rb %s" % (
        self.config.get_path(type="business_object"), self.config.get_path(type="service_object"), thrift_file)
        exit_code = subprocess.call(shlex.split(cmd))
        if exit_code != 0:
            self.log("failed to compile thrift file %s" % thrift_file)
            sys.exit(exit_code)

        self.log("Building ruby class for %s" % thrift_file)


    def is_service(self, thrift_file):
        """
         boolean check on thrift file whether true if it contains the service_prefix in the file name.

         Usually it's 'service' or whatever you overrode the value with in the config file.
        """
        if thrift_file.find(self.config.get_global_option("service_prefix")) != -1:
            return True
        else:
            return False


    def thrift_build(self, thrift_file, language="java"):
        """
            compiles a single thrift file and copies content to
            maven structure for consumption.
        """
        if self.build.has_key(language):
            self.build.get(language)(thrift_file)

    def get_thrift_full_path(self, thrift_file):
        if thrift_file is None:
            return None

        if thrift_file.find("/") >= 0:
            return thrift_file

        if thrift_file.find(self.config.get_global_option("service_prefix")) != -1:
            return os.path.join(self.config.get_path(type="service_object"), thrift_file)
        else:
            return os.path.join(self.config.get_path(type="business_object"), thrift_file)


    def read_thrift_dependencies_recursively(self, thrift_file):
        dependencies = set(self.read_thrift_dependencies(thrift_file))
        if len(dependencies) is 0:
            return set()
        for item in dependencies:
            dependencies = dependencies.union(set(self.read_thrift_dependencies_recursively(item)))

        return dependencies


    def read_thrift_dependencies(self, thrift_file):
        """
            Parse a thrift file and extract the includes returning it as a list of
            it's dependencies.
        """
        self.log("Processing %s" % thrift_file)
        is_enum = False
        is_exception = False
        thrift_file = self.get_thrift_full_path(thrift_file)
        self.check_file(thrift_file)
        f = open(thrift_file, 'r')
        data = f.readlines()
        f.close()
        includes = []
        object_count = 0
        for line in data:
            #skip comments
            if line.startswith("#"):
                continue
            if line.startswith("enum"):
                is_enum = True
            if line.startswith("exception"):
                is_exception = True
            if line.startswith("include"):
                line = line.strip()
                begin = line.find("\"")
                end = line.find("\"", begin + 1)
                includes.append(line[begin + 1:end])
            if line.startswith("struct") or line.startswith("enum") or line.startswith("exception"):
                object_count += 1

        if object_count > 1:
            self.log(
                "tsk..tsk..tsk, you tried to build an object {file} that contained multiple structs/enums.".format(
                    file=thrift_file))
            sys.exit(1)

        if is_enum:
            ndx = thrift_file.find(self.config.get_global_option("enum_prefix"))
            if ndx < 0:
                self.log("error, any enum should be defined inside a .enum file")
                sys.exit(1)

        if is_exception:
            ndx = thrift_file.find(self.config.get_global_option("exception_prefix"))
            if ndx < 0:
                self.log("error, any exception should be defined inside a .exception file")
                sys.exit(1)

        return includes

    def read_thrift_properties(self, thrift_file):
        """
            Given a thrift file it will return the groupid, version and artifact name
            as hashmap/dictionary.
        """
        thrift_file = self.get_thrift_full_path(thrift_file)
        if not os.path.exists(thrift_file):
            return {}
        meta_data = {}
        f = open(thrift_file)
        raw = f.read()
        f.close()

        meta_data["VERSION"] = self.__extract_string__(pattern="VERSION", raw=raw, default="0.0.0")
        meta_data["GROUPID"] = self.__extract_string__(pattern="GROUPID", raw=raw,
                                                     default=self.config.get_global_option("group_id"))
        meta_data["ARTIFACTID"] = self.get_object_name(thrift_file)

        return meta_data

    @staticmethod
    def __extract_string__(pattern, raw, default=None):
        """
            Given a text line it will try to extract the value from a thrift constant matching the pattern passed in.
        """
        match = re.search(".*%s.*=" % pattern, raw)
        if match is None:
            return default
        start = match.start() + len(match.group(0))
        end = raw.find("\n", start)
        if start == -1 or end == -1:
            return default
        result = re.sub("[',\"]", "", raw[start:end]) # remove quotes
        return re.sub("#.*", "", result).strip()

    def get_object_name(self, raw, delimter="-"):
        """
        Build an artifact name from a filename.

        ie.  given wizecommerce.bizobj.foobar.example.thrift it should return  foobar-example-bizobj
             given wizecommerce.services.foobar.example.thrift it should return  foobar-example-client
        """
        raw = os.path.basename(raw).replace(".thrift", "")
        pattern = "{company_name}.".format(company_name=self.config.get_global_option("company_name"))
        ndx = raw.find(pattern)
        if ndx < 0:
            print("could not find company prefix pattern: {pattern}".format(pattern=pattern))
            sys.exit(ndx)
        raw = raw[ndx + len(pattern):]
        ndx = raw.find(".")
        if ndx < 0:
            print("could not find delimiter in file name")
            sys.exit(ndx)

        postfix = raw[:ndx]
        if postfix == self.config.get_global_option("service_prefix"):
            postfix = "client"
            raw = raw.replace(self.config.get_global_option("service_prefix") + ".", "")
        else:
            raw = raw.replace(postfix + ".", "")

        raw = raw.replace(".", delimter) + delimter + postfix
        return raw


class ThriftCompiler(object):
    """
    This should allow support for multiple thrift compilers.  Passing in specialized options etc.  This part of the code
    isn't really used yet, and is mainly a placeholder for now.
    """

    def __init__(self, properties):
        self.meta_data = {}
        self.meta_data = properties.copy()

    @property
    def version(self):
        return self.meta_data.get("version")

    @version.setter
    def version(self, value):
        self.meta_data['version'] = value


    @property
    def name(self):
        return self.meta_data.get("name")

    @name.setter
    def name(self, value):
        self.meta_data['name'] = value

    @property
    def bin(self):
        return self.meta_data.get("bin")

    @bin.setter
    def bin(self, value):
        self.meta_data['bin'] = value


    @property
    def options(self):
        return self.meta_data.get("options")

    @options.setter
    def options(self, value):
        self.meta_data['options'] = value

    @property
    def languages(self):
        return self.meta_data.get("supported_languages")

    @languages.setter
    def languages(self, value):
        self.meta_data['supported_languages'] = value

    def is_language_supported(self, value):
        for lang in self.languages:
            if lang == value:
                return True
        return False

