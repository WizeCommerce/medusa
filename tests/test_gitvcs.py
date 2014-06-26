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
import unittest
import unittest2
from thrift_medusa.utils.config import Config
from thrift_medusa.vcs.GitVCS import GitVCS


class GitVCSTests(unittest2.TestCase):
    def setUp(self):
        self.config = Config()
        init_data = {}
        self.gitcvs = GitVCS(**init_data)

    def tearDown(self):
        self.config.reset_configuration()

    def test_find_commit(self):
        commits = self.gitcvs.get_commits()
        self.failIf(len(commits) == 0)
        expected = commits[0]
        result = self.gitcvs.find_commit(str(expected))[0]
        self.assertEquals(result.hexsha, expected.hexsha)
        self.assertEquals(type(result), type(expected))

    def test_git_stub(self):
        commit_hash = "76191292fe70015eeee241fb9b663af6953ffb5e"
        commits = self.gitcvs.get_commits()
        data = self.gitcvs.find_commit(commit_hash)

        if data is not None and len(data) > 2:
            commitA = data[0]
            commitB = commits[data[1] + 1]
            files_list = self.gitcvs.get_modified_files(commitB, commitA, None)
            expected_files = set()
            expected_files.add(".travis.yaml")
            expected_files.add(".travis.yml")
            expected_files.add("README.md")
            expected_files.add("build_thrift.sh")
            expected_files.add("setup.py")
            expected_files.add("thrift_medusa/config/travis-ci.yaml")
            for item in files_list:
                self.assertTrue(item in expected_files)


if __name__ == "__main__":
    # Run unit tests
    suite = unittest2.TestLoader().loadTestsFromTestCase(GitVCSTests)
    unittest2.TextTestRunner(verbosity=2).run(suite)
