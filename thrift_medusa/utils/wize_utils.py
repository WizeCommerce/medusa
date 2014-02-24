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
import os
import paramiko
import string

class WizeUtilities():

    def __init__(self):
        pass

    @staticmethod
    def wize_mkdir(newdir):
        """works the way mkdir -p should :)
            - already exists, silently complete
            - regular file in the way, raise an exception
            - parent directory(ies) does not exist, make them as well
        """
        if os.path.isdir(newdir):
            pass
        elif os.path.isfile(newdir):
            raise OSError("a file with the same name as the desired " \
                          "dir, '%s', already exists." % newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head):
                WizeUtilities.wize_mkdir(head)
            if tail:
                os.mkdir(newdir)

    @staticmethod
    def build_file_list(location, filters):
        """
            Given a directory it will list all files that match a particular
            set of filters.
        """
        files = []
        for (dir_path, dir_name, file_names) in os.walk(location):
            for item in file_names:
                files.append(os.path.join(dir_path, item))
        object_list = map(lambda file: os.path.join(location, file), files)

        if type(filters) == list:
            for file_filter in filters:
                object_list = [i for i in object_list if file_filter in i]
        else:
            object_list = [i for i in object_list if filters in i]

        return object_list

    @staticmethod
    def wize_sshmkdir(**kwargs):
        """
        Will ssh to remote server and create the remote directory
        """

        ssh = paramiko.SSHClient()
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(hostname=kwargs['host'], username=kwargs['user'])
        if kwargs.get('strip_file', False):
            ssh.exec_command("mkdir -p %s" % os.path.dirname(kwargs['remote_path']))
        else:
            ssh.exec_command("mkdir -p %s" % kwargs['remote_path'])


    @staticmethod
    def wize_scp(**kwargs):
        """
        Will create destination directory if it doesn't exist and scp localpath to remotepath
        """
        try:
            if 'remote_path' in kwargs:
                kwargs['strip_file'] = True
                WizeUtilities.wize_sshmkdir(**kwargs)
            ssh = paramiko.SSHClient()
            ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=kwargs['host'], username=kwargs['user'])
            sftp = ssh.open_sftp()
            sftp.put(kwargs['local_path'], kwargs['remote_path'])
            sftp.close()
            ssh.close()
            return 0
        except:
            return -1


    @staticmethod
    def increment_version(version):
        """
            Given a version in either of the following formats:
                1
                1.0.0.5  (with any number of decimal points)
            This function will increment the small denominator and bump it up by 1
        """

        if version.find(".") == -1:
            try:
                num = int(version)
                num += 1
                return str(num)
            except ValueError:
                return -1

        groups = version.split(".")
        last_tuple = groups[len(groups) - 1]
        try:
            num = int(last_tuple)
            num += 1
            #combine
            groups[len(groups) - 1] = str(num)
            result = string.join(groups, ".")
            return result

        except ValueError:
            return "-1"


