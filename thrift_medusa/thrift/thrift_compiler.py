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

from thrift_medusa.utils.config import Config


class ThriftCompiler(object):
    """
    This should allow support for multiple thrift compilers.  Passing in specialized options etc.  This part of the code
    isn't really used yet, and is mainly a placeholder for now.
    """

    def __init__(self, properties):
        self.config = Config()
        self.meta_data = properties.copy()

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
    def version(self):
        try:
            return self.meta_data["version"]
        except:
            return "0.6.1"  ##our default version

    @version.setter
    def version(self, value):
        self.meta_data["version"] = value

    def language_options(self, language="java"):
        try:
            return self.meta_data.get("language_options").get(language)
        except:
            #fallback on global options.
            try:
                data = self.config.get_thrift_option("global_compiler_options")
                return data[language]
            except:
                return None


    @property
    def languages(self):
        return self.meta_data.get("supported_languages")

    @languages.setter
    def languages(self, value):
        self.meta_data['supported_languages'] = value

    def is_language_supported(self, value):
        if self.languages is None:
            return False

        for lang in self.languages:
            if lang == value:
                return True
        return False

    @property
    def postfix(self):
        try:
            return self.meta_data["compiler_postfix"]
        except:
            return ""

    @postfix.setter
    def postfix(self, value):
        self.meta_data["compiler_postfix"] = value



