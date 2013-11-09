import os
import shlex
import subprocess
import re
import urllib2
from lib.clients.client import Client
from lib.utils.wize_utils import wize_mkdir


class JSClient(Client):

    def initialize(self):
        self.sandbox = os.path.join(self.config.work_dir, "%s/js" % self.compiler.name)
        self.sandbox_work = os.path.join(self.config.work_dir, "%s/js_work" % self.compiler.name)
        wize_mkdir(self.sandbox)
        wize_mkdir(self.sandbox_work)


    def __build_dependency__(self, business_object):
        """
            Recursively build the dependency and return a list of all dependencies found and successfully built.
        """
        self.thrift_helper.check_file(business_object)
        self.thrift_helper.thrift_build(thrift_file=business_object, language="js", sandbox=self.sandbox_work)

        properties = self.thrift_helper.read_thrift_properties(business_object)
        self.deploy_object(properties, business_object)
        return 0


    def __deploy_local_artifact__(self, properties, thrift_object, postfix=""):
        pass

    def __deploy_production_artifact__(self, properties, thrift_object, postfix=""):
        pass

    def __build_client__(self, service):
        pass


    def finalize(self):
        pass


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
            if not kwargs.has_key("groupId") or not kwargs.has_key("artifactId") or not kwargs.has_key("version"):
                self.log("missing arguments, Please check your logic thrift file configuration for %s%" % kwargs)
                return
            properties = kwargs

        if properties['groupId'] is None or properties['artifactId'] is None or properties['version'] is None:
            return False

        properties['groupId'] = properties.get('groupId').replace(".", "/")

        url = self.config.get_js_option("www_base_url") + properties['groupId'] + "/" + properties[
            'artifactId'] + "/" + str(properties['version']) + "/" + self.generate_artifact_name(
            groupId=properties['groupId'], artifactId=properties['artifactId'], version=properties['version'])

        try:
            ret = urllib2.urlopen(url)
            boolean_check = True
            if ret.code == 200:
                boolean_check = False
            else:
                self.log("%s doesn't exists" % url)

            ret.close()
            return boolean_check
        except:
            self.log("%s doesn't exists" % url)
            return True


        return True

