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

import subprocess
from thrift_medusa.utils.log import Log
from thrift_medusa.utils.config import Config
from thrift_medusa.utils.wize_utils import *
import shlex
import re
import sys


class Thrift():
    def __init__(self, compiler):
        self.compiler=compiler
        self.version_pattern = re.compile("const\s+string\s+VERSION\s*=\s*['\"]+(.*)['\"]+")
        self.java_namespace_pattern = re.compile("namespace\s+java\s+(.*)")
        self.ruby_namespace_pattern = re.compile("namespace\s+rb\s+(.*)")
        self.data_type_pattern = re.compile("\s+(\d+):\s+([required,optional]+)\s+([bool,byte,i16,i32,i64,string,double,string]+)\s+(\w+)")

        self.config = Config()
        self.log = Log(log_file="status.log", logger_name="status").log
        # defines the language compiler to spawn.
        self.build = {"ruby": self.__thrift_ruby_build__, "java": self.__thrift_java_build__,
                      "doc": self.__thrift_doc_build__}

    def __setup_maven__(self, sandbox="default"):
        """
            removes the old maven structure, and recreates it
        """
        if sandbox == "default":
            sanbox = self.config.work_dir

        os.system("rm -fr %s" % (os.path.join(sandbox, "src")))
        os.system("rm -f %s" % os.path.join(sandbox, "pom.xml"))
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


    def __thrift_java_build__(self, thrift_file, sandbox="default"):
        """
        compile the thrift file passed in to java format.
        :param thrift_file:
        """
        if sandbox == "default":
            sandbox = self.config.work_dir
        thrift_file = self.get_thrift_full_path(thrift_file)
        os.system("rm -fr %s" % os.path.join(sandbox, self.config.java_sandbox))
        os.chdir(sandbox)
        self.log("Building java class for %s" % thrift_file)
        cmd = "{thrift_binary} -I {business_objects} -I {services} {options} {language_options} {file}".format(
            business_objects=self.config.get_path(type="business_object"),
            services=self.config.get_path(type="service_object"), thrift_binary=self.compiler.bin,
            file=thrift_file, options=self.compiler.options, language_options=self.compiler.language_options("java"))

        exit_code = subprocess.call(shlex.split(cmd))
        if not exit_code == 0:
            self.log("failed to compile thrift file {file}".format(file=thrift_file))
            sys.exit(1)

    def __thrift_doc_build__(self, thrift_file, sandbox="default"):
        if sandbox == "default":
            sandbox = self.config.work_dir
        thrift_file = self.get_thrift_full_path(thrift_file)
        os.system("rm -fr %s" % os.path.join(sandbox, self.config.doc_sandbox))
        wize_mkdir(self.config.doc_sandbox)

        full_path = self.get_thrift_full_path(thrift_file)
        dependencies = self.read_thrift_dependencies_recursively(full_path)
        for item in dependencies:
                file = self.get_thrift_full_path(item)
                cmd = "{thrift_binary} -I {business_objects} -I {services} {options} {language_options} -o {destination} {file} ".format(
                        business_objects=self.config.get_path(type="business_object"),
                        services=self.config.get_path(type="service_object"), thrift_binary=self.compiler.bin,
                        file=file, options=self.compiler.options, language_options=self.compiler.language_options("doc"),
                        destination=sandbox)
                exit_code = subprocess.call(shlex.split(cmd))
                if not exit_code == 0:
                    self.log("failed to compile thrift dependency {dependency} for file {file}".format(dependency=file,file=file))
                    sys.exit(1)


        self.log("Generating documentation for %s" % thrift_file)

        cmd = "{thrift_binary} -I {business_objects} -I {services} {options} {language_options} -o {destination} {file}".format(
            business_objects=self.config.get_path(type="business_object"),
            services=self.config.get_path(type="service_object"), thrift_binary=self.compiler.bin,
            file=thrift_file, options=self.compiler.options, language_options=self.compiler.language_options("doc"), destination=sandbox)

        exit_code = subprocess.call(shlex.split(cmd))
        if not exit_code == 0:
            self.log("failed to compile thrift file {file}".format(file=thrift_file))
            sys.exit(1)


    def __thrift_ruby_build__(self, thrift_file, sandbox="default"):
        """
        compile the thrift file passed in to ruby format.
        :param thrift_file:
        """
        if sandbox == "default":
            sandbox = self.config.work_dir

        os.system("rm -fr %s" % os.path.join(sandbox, self.config.java_sandbox))
        os.chdir(sandbox)
        thrift_file = self.get_thrift_full_path(thrift_file)
        os.system("rm -fr %s" % (self.config.get_ruby_option("sandbox", True)))
        os.system("rm -fr %s" % (os.path.join(self.config.work_dir, "ruby")))
        cmd = "{thrift_binary} -I {business_objects} -I {services} {options} {language_options}   {file}".format(
            business_objects=self.config.get_path(type="business_object"),
            services=self.config.get_path(type="service_object"), thrift_binary=self.compiler.bin,
            file=thrift_file, options=self.compiler.options, language_options=self.compiler.language_options("ruby"))
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


    def thrift_build(self, thrift_file, language="java", sandbox="default"):
        """
            compiles a single thrift file and copies content to
            maven structure for consumption.
        """
        if sandbox == "default":
            sandbox = self.config.work_dir
        if self.build.has_key(language):
            self.build.get(language)(thrift_file, sandbox)

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


    def check_constraints(self, line, thrift_file, diff):
        if self.config.get_thrift_constraint("constraints_enabled"):
            if self.config.get_thrift_constraint("enforce_empty"):
                match = re.search("bool.*empty", line)
                if match is not None and line.find("required") == -1:
                    self.log("Error: bool empty field must be a required field. Missing in file {file}".format(file=thrift_file))
                    sys.exit(1)
            if self.config.get_thrift_constraint("visibility_check"):
                if line.find("bool") >= 0 or line.find("i64") >= 0 or line.find("i32") >= 0 or \
                    line.find("byte") >= 0 or line.find("double") >= 0 or line.find("string") >= 0:
                        if line.find("optional") == -1 and line.find("required") == -1 and line.find("VERSION") == -1:
                            self.log("Error: package visibility flag omitted for line: {line} in file: {file}.".format(line=line.replace("\n",""), file=thrift_file))
                            sys.exit(1)
            ## Needs git support.
            if self.config.get_thrift_constraint("check_field_ordering"):
                pass
            if self.config.get_thrift_constraint("check_version_increment"):
                if diff is not None and diff != "" and diff.find("VERSION") == -1:
                    self.log("Error, You forgot to increment the version for {file}".format(file=thrift_file))
                    sys.exit(1)


                pass
        else:
            pass

    def decipher_thrift_file(self, thrift_file):
        """
        This method will read a thrift file and pull out any data that we understand
        for further logic processing.

        ie.  numeric index, type, field name, VERSION constant etc.

        """
        if self.is_service(thrift_file):
            return {}

        thrift_file = self.get_thrift_full_path(thrift_file)
        self.check_file(thrift_file)
        fp = open(thrift_file, 'r')
        data = fp.readlines()
        fp.close()
        thrift_meta = {}
        for line in data:
            match = self.version_pattern.match(line)
            if match is not None:
                thrift_meta['version'] = match.group(1)
            match = self.java_namespace_pattern.match(line)
            if match is not None:
                thrift_meta['java_namespace'] = match.group(1)
            match = self.ruby_namespace_pattern.match(line)
            if match is not None:
                thrift_meta['ruby_namespace'] = match.group(1)
            match = self.data_type_pattern.match(line)
            if match is not None:
                if match.lastindex != 4:
		    self.log("Error: found a discrepancy when parsing {file}".format(thrift_file=file))
                    sys.exit(1)
                type = {}
                type['visibility'] = match.group(2)
                type['type'] = match.group(3)
                type['name'] = match.group(4)
                thrift_meta[match.group(1)] = type


        return thrift_meta




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
        fp = open(thrift_file, 'r')
        data = fp.readlines()
        fp.close()
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
        meta_data["GROUPID"] = self.__extract_string__(pattern="GROUPID", raw=raw, default=self.config.get_global_option("group_id"))
        meta_data["ARTIFACTID"] = self.get_object_name(thrift_file)

        return meta_data

    @staticmethod
    def __extract_string__(pattern, raw, default=None):
        """
            Given a text line it will try to extract the value from a thrift constant matching the pattern passed in.
        """
        match = re.search(".*{search_pattern}.*=".format(search_pattern=pattern), raw)
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
	    self.log("could not find company prefix pattern: {pattern}".format(pattern=pattern))
            sys.exit(ndx)
        raw = raw[ndx + len(pattern):]
        ndx = raw.find(".")
        if ndx < 0:
            self.log("could not find delimiter in file name")
            sys.exit(ndx)

        postfix = raw[:ndx]
        if postfix == self.config.get_global_option("service_prefix"):
            postfix = "client"
            raw = raw.replace(self.config.get_global_option("service_prefix") + ".", "")
        else:
            raw = raw.replace(postfix + ".", "")

        raw = raw.replace(".", delimter) + delimter + postfix
        return raw



