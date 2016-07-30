'''
Created on Jul 30, 2016

@author: Petr Muller
'''

import git

class GitRepoIterator(object):
    """
    Iterates over a Git repository.

    Each iteration checks out the first parent of the current commit
    and returns the SHA of the parent.
    """
    def __init__(self, repo_path, start, finish):
        self.repo = git.Repo(repo_path)
        self.repo_direct = git.Git(repo_path)

        self.start = start
        self.finish = finish

        self.last = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.last == self.finish:
            raise StopIteration

        if self.last is None:
            self.repo_direct.checkout(self.start)
            self.last = self.start
            return self.last

        last = self.repo.commit(self.last)
        parent = last.parents[0].hexsha
        self.repo_direct.checkout(parent)
        self.last = parent
        return self.last
