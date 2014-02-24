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
from thrift_medusa.models.server import Server

__author__ = 'sfaci'

import os
import shlex
import sys
from thrift_medusa.utils.wize_utils import WizeUtilities
from thrift_medusa.clients.client import Client
from thrift_medusa.utils.naming_helper import cap_convert
import subprocess
import re
from jinja2 import Template

class RubyClient(Client):

    def initialize(self):
        self.sandbox = os.path.join(self.config.work_dir, "%s/ruby" % self.compiler.name)
        WizeUtilities.wize_mkdir(self.sandbox)
        os.putenv("GEM_HOME", self.sandbox)  # Allows local installs

    def check_version(self, **kwargs):
        """
            Returns a boolean checking if the artifact exists on the deployment server.
            True:  deploy version
            False: already deployed.
        """
        if self.config.is_local():
            return True

        if kwargs is None or len(kwargs) == 0:
            self.log("No arguments received")
            return False
        else:
            if "artifactId" not in kwargs or "version" not in kwargs:
                self.log("missing arguments, Please check your logic thrift file configuration for %s" % kwargs)
                return
            properties = kwargs

        if properties['artifactId'] is None or properties['version'] is None:
            return False

        url = self.config.get_ruby_path_option(key="host")
        gem = properties['artifactId']

        cmd = shlex.split("gem list  --source {source} -r {gem}".format(source=url, gem=gem))
        p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(shlex.split("grep '{pattern} '".format(pattern=gem)), stdin=p1.stdout,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p2.communicate()[0]
        out = re.sub(".*\(", "", out )
        out = re.sub("\)", "", out)
        out = out.split(",")[0]

        if out.strip() == properties['version']:
            self.log("%s-%s has already been deployed to server" % (gem, properties['version']))
            return False

        return True

    @staticmethod
    def fix_properties(properties):
        """
        Ruby uses underscores rather then dashes.  This fixes the java behavior in the names.
        It also replaces . with /
        Fix _
        """
        key = "ARTIFACTID"
        if key not in properties:
            return properties

        raw = properties.get(key).replace("-", "_")
        properties[key] = raw

        key = "GROUPID"
        if key not in properties:
            return properties
        raw = properties.get(key).replace(".", "/")
        properties[key] = raw
        return properties

    def __deploy_production_artifact__(self, properties, thrift_object, postfix=""):
        """
            Implement a method responsible for deploying your artifact to your production server.
        """
        if self.status.is_deployed(properties.get("ARTIFACTID"), properties.get("VERSION"), "ruby"):
            return 0

        self.__deploy_local_artifact__(properties, thrift_object, postfix)

        check_value = self.check_version(artifactId=properties.get("ARTIFACTID"),
                                        version=properties.get("VERSION"))

        if check_value:
            file = properties.get("ARTIFACTID") + "-" + properties.get("VERSION") + ".gem"
            exit_code = self.__sshDeployArtifact__(os.path.join(self.config.work_dir, "ruby", file))
            if exit_code != 0:
                self.log("Failed to deploy artifact {artifact}".format(artifact=os.path.join(self.config.work_dir,
                                                                                             "ruby", file)))
                sys.exit(exit_code)

        return exit_code

    def __sshDeployArtifact__(self, file):
        """
            copy gem file to remote repo and installs gem.
        """
        self.log(file)
        ssh_config = self.config.get_ruby_option(key="ssh_server").copy()
        ssh_config['local_path'] = file
        ssh_config['remote_path'] = os.path.join(ssh_config['remote_path'], os.path.basename(file))
        server = Server(**ssh_config)
        exit_code = WizeUtilities.wize_scp(**server.dictionary.copy())
        if exit_code != 0:
            self.log("failed to copy gem file {gem_file} to remote server".format(gem_file=os.path.basename(file)))
            sys.exit(exit_code)
        self.log("successfully copied {gem_file} to remote server".format(gem_file=file))
        #install gem
        ## -t -t setups a fake tty mode
        cmd = "ssh -t -t {user}@{host} 'sudo gem install {gem_file}'".format(user=server.user, host=server.host,
                                                                             gem_file=server.remote_path)
        self.log("executing:  " + cmd)
        status = os.system(cmd)

        if status != 0:
            self.log("Failed to install %s on remote server" % file)
        self.log("succeeded at executing:  " + cmd)
        #Cleanup
        cmd = "ssh  {user}@{host} 'rm -v {directory}/*.gem'".format(user=server.user, host=server.host, directory=os.path.dirname(server.remote_path))
        os.system(cmd)
        return 0


    def thrift_ruby_fixes(self, properties):
        """
            updates relative paths, writes a gem level .rb file which
            imports all related .rb files.

            import all dependencies of gem as well in the global level .rb file

        """
        results = WizeUtilities.build_file_list(self.config.get_ruby_path_option("sandbox"), ".rb")
        WizeUtilities.wize_mkdir(self.config.get_ruby_path_option("ruby"))
        group_id = properties.get("ARTIFACTID")
        destination = os.path.join(self.config.get_ruby_path_option("ruby"), group_id)
        require_check = re.compile("require")
        #find VERSION followed by n.n.n where n is any digit from 0-9 that repeats as many times as desired.
        version_check = re.compile(".*VERSION.*\d+\.\d+\.\d+")
        results_check = {}
        for file in results:
            results_check[os.path.basename(file).replace(".rb", "")] = True
        for file in results:
            f = open(file, 'r')
            lines = f.readlines()
            f.close()
            for ndx in range(0, len(lines)):
                line = lines[ndx]
                requires_result = require_check.match(line)
                version_result = version_check.match(line)
                if requires_result is not None:
                    start = line.find("'") + 1
                    end = line[start:].find("'")
                    key = line[start:start + end]
                    if key in results_check:
                        line = "require '%s'\n" % os.path.join(group_id, line[start:start + end])
                        lines[ndx] = line
                    else:
                        lines[ndx] = ""
                elif version_result is not None:
                    start = line.find("'") + 1
                    end = line[start:].find("'")
                    lines[ndx] = "VERSION = %%q\"%s\"" % properties.get("VERSION")
                    #lines.insert(0, "require 'thrift'\n")
            outfile = os.path.join(destination, os.path.basename(file))
            WizeUtilities.wize_mkdir(os.path.dirname(outfile))
            new_file = open(outfile, 'w')
            new_file.writelines(lines)
            new_file.close()

        ##setup loader class
        file = os.path.join(self.config.get_ruby_path_option("ruby"), properties.get("ARTIFACTID") + ".rb")
        loader = open(file, 'w')
        loader.write("require 'thrift'\n")
        ##inject a require
        for f in self.thrift_helper.read_thrift_dependencies(properties.get("THRIFT")):
            loader.write(
                "require '%s'\n" % self.thrift_helper.read_thrift_properties(f).get("ARTIFACTID").replace("-", "_"))

        for file in results:
            f = os.path.basename(file)
            loader.write("require '" + os.path.join(group_id, f) + "'\n")

        loader.close()

    def __deploy_local_artifact__(self, properties, thrift_object, postfix=""):
        """
            Implement a method responsible for performing a local install.
        """

        os.system("rm -fr {ruby_work}".format(ruby_work=os.path.join(self.config.work_dir, "ruby")))
        properties["THRIFT"] = thrift_object

        #ensures that this particular gems hasn't already been built.
        if self.status.is_deployed(properties.get("ARTIFACTID"), properties.get("VERSION"), "ruby"):
            self.log(
                "%s-%s has already been built, skipping" % (
                    properties.get("ARTIFACTID"), properties.get("VERSION")))
            return 0
        else:

            self.thrift_helper.thrift_build(thrift_file=thrift_object, sandbox=self.sandbox_work, language="ruby")
            # self.thrift_helper.thrift_build(thrift_file=thrift_object, language="ruby")
            self.thrift_ruby_fixes(properties)

        config = self.config.config_dir
        #install gemFile and Rakefile
        for file in ["Example.Gemfile", "Example.Rakefile"]:
            src = os.path.join(config, file)
            dest = os.path.join(self.config.work_dir, "ruby", file.split(".")[1])
            fp = open(src, 'r')
            raw = fp.read()
            fp.close()
            template = Template(raw)
            raw = template.render(RUBYGEMS=self.config.get_ruby_option("host", True))
            fp = open(dest, 'w')
            fp.write(raw)
            fp.close()

        self.__update_gem_spec__(os.path.join(config, "Example.gemspec"), properties)
        os.chdir("ruby")
        gemspec_file = properties.get("ARTIFACTID") + ".gemspec"
        cmd = ['gem', 'build', gemspec_file]

        self.local_assert(subprocess.call(cmd), "Failed to execute {cmd}".format(cmd=cmd))

        file = properties.get("ARTIFACTID") + "-" + properties.get("VERSION") + ".gem"
        cmd = ['gem', 'install', file]
        self.local_assert(subprocess.call(cmd), "Failed to execute {cmd}".format(cmd=cmd))

        os.system("cp -v *.gem %s" % self.sandbox)

        self.status.add_artifact(version=properties.get("VERSION"), artifact=properties.get("ARTIFACTID"), lang="ruby")
        os.chdir(self.config.work_dir)
        ##TODO: insert deploying of 'snapshot' versions here once a feature request for a dev version is requested.

        return 0

    def __update_gem_spec__(self, file, properties):
        """
            Inject Example.gemspec with appropriate values, replace the wildcard
            values with the calculated run time values.
        """
        if not os.path.exists(file):
            self.log("{file} does not exist".format(file=file))
            sys.exit(1)

        fp = open(file, 'r')
        raw = fp.read()
        fp.close()
        file_list = WizeUtilities.build_file_list(self.config.get_ruby_path_option("ruby"), ".rb")
        version_file = None
        for fp in file_list:
            if fp.find("constants") >= 0:
                version_file = fp.replace(self.config.get_ruby_path_option("ruby") + "/", "").replace(".rb", "")

        template = Template(raw)
        raw = template.render(WIZECAMELNAME=cap_convert(properties.get("ARTIFACTID")),
                              WIZENAME=properties.get("ARTIFACTID"), WIZEDEPENDENCY=properties.get("GEM"),
                              WIZECONSTANTS=version_file, WIZEAUTHOR=self.config.get_ruby_option("author"),
                              WIZEEMAIL=self.config.get_ruby_option("email"), WIZESCM=self.config.get_ruby_option("scm"))

        out_file = os.path.join(self.config.work_dir, "ruby", properties.get("ARTIFACTID") + ".gemspec")
        out = open(out_file, 'w')
        out.write(raw)
        out.close()


    def __build_dependency__(self, thrift_file):
        """
            called by base class and builds all dependencies and deploy the artifact
            either locally or globally based on env. settings.
        """
        self.thrift_helper.check_file(thrift_file)

        properties = self.thrift_helper.read_thrift_properties(thrift_file)
        object_dependencies = self.thrift_helper.read_thrift_dependencies(thrift_file)
        if object_dependencies is not None and len(object_dependencies) > 0:
            for dependency in object_dependencies:
                self.__build_dependency__(dependency)

        properties["GEM"] = self.__generateInjectionCode__(thrift_file)
        ##fix artifactID
        properties = self.fix_properties(properties)


        #build Gem file
        return self.deploy_object(properties, thrift_file)

    def __generateInjectionCode__(self, thrift_file):
        """
            Generates the code to be injected into the gemspec file.
        """
        object_dependencies = self.thrift_helper.read_thrift_dependencies(thrift_file)
        dependencies = ""
        for object in object_dependencies:
            properties = self.thrift_helper.read_thrift_properties(object)
            version = properties.get("VERSION")
            gem_name = properties.get("ARTIFACTID").replace("-", "_")
            dependencies += 'spec.add_dependency "%s", "~> %s"\n' % (gem_name, version)

        return dependencies

    def __build_client__(self, thrift_file):
        """
            build the service thrift file
        """
        self.log("buildRuby Client has been called for %s " % thrift_file)
        self.thrift_helper.check_file(thrift_file)
        os.chdir(self.config.work_dir)

        properties = self.thrift_helper.read_thrift_properties(thrift_file)
        #serviceDependencies = self.thriftHelper.readThriftDependencies(thriftFile)
        properties = self.fix_properties(properties)  ## replace - with _
        properties["GEM"] = self.__generateInjectionCode__(thrift_file)

        #build Gem file
        return self.deploy_object(properties, thrift_file)

    def finalize(self):
        pass


def __update_version__(file, properties):
    """
        This will only be used if we have a devel version.  For now,
        it's simply a place holder.
    """
    pass
    # assert os.path.exists(file), self.log("%s does not exist", file)
    # f = open(file, 'r')
    # raw = f.read()
    # f.close()
    #
    # properties["VERSION"] = properties.get("VERSION").replace("-SNAPSHOT", "")
    #
    # raw = raw.replace("WIZENAMECAMEL", capConvert(properties.get("ARTIFACTID"))).replace("WIZEVERSION",
    #                                                                                      properties.get("VERSION"))
    # wizemkdir(os.path.join(self.config.get_ruby_option("ruby"), properties.get("ARTIFACTID")))
    # out = open(os.path.join(self.config.get_ruby_option("ruby"), properties.get("ARTIFACTID"), "version.rb"), 'w')
    # out.write(raw)
    # out.close()

