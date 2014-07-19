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

##Singlelton (The borg) pattern recipe from:
# http://code.activestate.com/recipes/66531/


class Status:
    """ the purpose of this class is to keep track of which artifacts have already
         been deployed and what hasn't.

         ie. try to only build an artifact once.

    """
    __shared_state = {}
    __deployed__ = {}

    @staticmethod
    def __build_key__(artifact, version, lang="java", compiler="thrift"):
        return artifact + "-" + version + "-" + lang + "-" + compiler

    def is_deployed(self, artifact, version, lang="java", compiler="thrift"):
        """
            expected format of "artifact" is artifact-version
        """
        id = self.__build_key__(artifact, version, lang, compiler)
        return self.__deployed__.has_key(id)

    def add_artifact(self, artifact, version, lang="java", compiler="thrift"):
        id = self.__build_key__(artifact, version, lang, compiler)
        self.__deployed__[id] = id

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        self.__dict__ = self.__shared_state

