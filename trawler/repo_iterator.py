'''
Created on Jul 30, 2016

@author: Petr Muller
'''

import re

import git
import logging


class GitRepoIterator(object):
    """
    Iterates over a Git repository.

    Each iteration checks out the first parent of the current commit
    and returns the SHA of the parent.
    """
    def __init__(self, repo_path, start, finish, only_paths=None):
        self.repo = git.Repo(repo_path)
        self.repo_direct = git.Git(repo_path)

        self.start = start
        self.finish = finish
        self.only_paths = only_paths

        self.last = None

    def __iter__(self):
        return self

    def is_included(self, commit):
        if self.only_paths is None:
            return True

        logging.debug("Considering commit '%s' against pattern '%s'",
                      commit.hexsha, self.only_paths)
        files_raw = self.repo_direct.execute(["git", "diff-tree",
                                              "--no-commit-id", "--name-only",
                                              "-r", commit.hexsha])
        files = files_raw.split("\n")

        for item in files:
            if re.match(self.only_paths, item):
                logging.debug("Commit matches pattern '%s' because of path '%s'",
                              self.only_paths, item)
                return True

        logging.debug("Commit '%s' does not match pattern '%s'", commit.hexsha,
                      self.only_paths)
        return False

    def __next__(self):
        if self.last == self.finish:
            raise StopIteration

        if self.last is None:
            candidate = self.repo.commit(self.start)
        else:
            candidate = self.repo.commit(self.last).parents[0]

        while not self.is_included(candidate):
            candidate = candidate.parents[0]

        self.repo_direct.checkout(candidate.hexsha)
        self.last = candidate.hexsha
        return self.last
