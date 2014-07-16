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


class VersionControlSystem:
    """
       The purpose of this class is to provide an interface that can be extended to implement support for any
       version control system.  The idea is that the .thrift files exist under version control and if you wish
       to enable VCS awareness then we can try to detect the files that have changed and only build the files
       that were modified.
    """

    def __init__(self, **kwargs):
        """Encouraged conventions:
            local_path:  contains path to .git folder or .vcs and such   ie.  $HOME/project/thrift_medusa.git
            remote_path: contains FQ path to remote path  ie.  git@github.com:WizeCommerce/medusa.git
            base_file_path:  contains base path of repo.  ie.  $HOME/project/thrift_medusa
        """
        pass

    def get_tags(self):
        raise NotImplementedError("Method 'get_tags' is not implemented")

    def get_modified_files(self, revisionA=None, revisionB=None):
        """
        Returns a list of changes files between 2 revisions.
        """
        raise NotImplementedError("Method 'get_modified_files' is not implemented")

    def get_file(self, revision, file_path):
        """
        Returns the full file data of a file for a particular revision.
        """
        raise NotImplementedError("Method 'get_file' is not implemented")

    def get_diff(self, revisionA, revisionB, file_path):
        """
        Returns a delta for a file between two revisions.
        """
        raise NotImplementedError("Method 'get_diff' is not implemented")

    def get_branches(self, **kwargs):
        """
          Returns a list of all branches, optionally pass in arguments to specify
          origin if DCS.  kwargs will probably be null for master/slave VCS
        """
        raise NotImplementedError("Method 'get_branches' is not implemented")

