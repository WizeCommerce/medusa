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
import shlex
from thrift_medusa.vcs.VersionControlSystem import VersionControlSystem
import git
import os
import inspect


class GitVCS(VersionControlSystem):
    def __init__(self, **kwargs):
        VersionControlSystem.__init__(self, **kwargs)
        git_repo_location = kwargs.get('repo_location')
        self.head = None
        self.prev = None
        self.commits = None
        if git_repo_location is None:
            project_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
                                        "../../")
            git_repo_location = os.path.realpath(os.path.join(project_path, ".git"))

        self.repo = git.Repo(git_repo_location)
        self.git_repo = git.Git(git_repo_location)
        self.get_head()  #initialize head/prev

    def __fetch_filtered_tags(self, tags, **kwargs):
        """
        Applies additional filtering / regex on tag list.
        """
        tag_filter = kwargs['tag_filter']
        exclusion = kwargs['exclusions'] if 'exclusions' in kwargs else ""
        filtered_tags = []
        for tag in tags:
            if tag_filter in tag.name:
                if exclusion in tag.name:
                    filtered_tags.append(tag)
                else:
                    filtered_tags.append(tag)
        #ignore non versioned tags.
        return filtered_tags

    def __fetch_sorted_tags(self, tags, **kwargs):
        if kwargs.get('descending'):
            print "sorted in descending order"

        print "sorting in ascending order"
        raise NotImplementedError("Sorting of Tags is not currently Supported")

    def get_tags(self, **kwargs):
        tags = self.repo.tags
        if len(kwargs) == 0:
            return tags

        if 'filer_name' in kwargs:
            return self.__fetch_filtered_tags(tags, kwargs)

        if 'sorted' in kwargs:
            return self.__fetch_sorted_tags(tags, kwargs)

    def get_commits(self):
        if self.commits is None:
            self.commits = list(self.repo.iter_commits())
        return self.commits

    def get_commits_between_tags(self, revisionA=None, revisionB="HEAD"):
        if revisionA is None:
            commits_list = self.get_commits()
            list_size = len(commits_list)
            revisionA = commits_list[list_size - 2]
            revisionB = commits_list[list_size - 1]

        if revisionB == "HEAD":
            raw = self.git_repo.execute(shlex.split("git cherry %s %s" % (revisionA.name, revisionB)))
        else:
            raw = self.git_repo.execute(shlex.split("git cherry %s %s" % (revisionA, revisionB)))

        commits = raw.split("\n")

        ## filter out empty and future tags.
        ## there can be tags that are based on different branches that are in the future from master's perspective.
        ## those tags are omitted
        commits = filter(lambda s: len(s) > 0 and s[0] != '-', commits)
        if len(commits) == 0:
            return
        hashes = map(lambda s: s.replace("+ ", "").replace("- ", "").strip(), commits)
        return hashes

    def get_head(self):

        if self.head is None:
            commits = self.get_commits()
            commits_len = len(commits)
            if commits_len == 0:
                return None
            if commits_len >= 1:
                self.head = commits[0]
            if commits_len >= 2:
                self.prev = commits[1]

        return self.head

    def find_commit(self, revsion):
        """
           Will return commit object and location.
        """
        if revsion is None:
            raise RuntimeError("Invalid revision received")

        index = 0
        for commit in self.commits:
            if revsion == commit.hexsha:
                return (commit, index)
            index += 1


    def get_modified_files(self, current_commit=None, previous_commit=None, filter_data=".thrift"):
        """
            returns a list of all hashes (ie commits) between the two tags passed into the method.

            If current_commit or previous_commit is empty, will fall back on default behavior and return
            list of modified files for latest commit.
        """
        if current_commit is None or previous_commit is None:
            diff_set = self.head.diff(self.prev.hexsha)
        else:
            if type(current_commit) == str:
                current_commit = self.head if current_commit == "HEAD" else self.find_commit(current_commit)[0]
            if type(previous_commit) == str:
                previous_commit = self.head if previous_commit == "HEAD" else self.find_commit(previous_commit)[0]

            diff_set = current_commit.diff(previous_commit)

        modified_files = set()
        if diff_set is not None and len(diff_set) > 0:
            for change in diff_set:
                if change is not None and change.a_blob is not None:
                    modified_files.add(change.a_blob.path)
                if change is not None and change.b_blob is not None:
                    modified_files.add(change.b_blob.path)
        unique_files = []
        map(lambda item: unique_files.append(item), modified_files)
        unique_files.sort()
        if filter_data is not None:
            file_list = filter(lambda s: filter_data in s, unique_files)
            return file_list
        return  unique_files

