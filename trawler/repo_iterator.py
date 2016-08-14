'''
Created on Jul 30, 2016

@author: Petr Muller
'''

import logging
import re

import git

class GenericStrategy(object):
    """
    Base class for strategies. Not intended for instantiation.
    """
    def __init__(self, repo_path, start, finish, only_paths):
        self.repo = git.Repo(repo_path)
        self.repo_direct = git.Git(repo_path)

        self.start = start
        self.finish = finish
        self.only_paths = only_paths

        self.last = None

    def __iter__(self):
        return self

    def __next__(self):
        # pylint: disable=no-self-use
        raise Exception("This class should not be instantiated directly")

    def is_included(self, commit):
        """
        Returns true if a commit would be returned while iterating.
        """
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

class PairStrategy(GenericStrategy):
    """
    Iterates over a Git repository.

    Each iteration returns a revision that is a member of a pair of commits
    of which one commit is the only parent of the other.
    """
    def __init__(self, repo_path, start, finish, only_paths):
        super(PairStrategy, self).__init__(repo_path, start, finish, only_paths)

        self.worklist = [start]
        self.return_queue = []

        self.visited = set()
        self.pairs = {}

    def __next__(self):
        if self.last == self.finish:
            raise StopIteration

        if self.return_queue:
            self.last = self.return_queue.pop()
            self.visited.add(self.last)
            return self.last

        while self.worklist:
            candidate_hash = self.worklist.pop(0)
            candidate_commit = self.repo.commit(candidate_hash)

            self.worklist.extend([parent.hexsha for parent in candidate_commit.parents])

            if len(candidate_commit.parents) == 1 and self.is_included(candidate_commit):
                parent_hash = candidate_commit.parents[0].hexsha

                if parent_hash not in self.visited:
                    self.return_queue.append(parent_hash)
                    self.visited.add(parent_hash)

                self.pairs[candidate_hash] = parent_hash

                if candidate_hash not in self.visited:
                    self.visited.add(candidate_hash)
                    self.last = candidate_hash
                    return self.last
            else:
                logging.debug("Skipping commit %s", candidate_hash)

        raise StopIteration

    def write_data(self, directory_path):
        """
        Writes additional data about the strategy execution into a given directory.

        Writes the pairs in the parent->child format into a 'pairs' file.
        """
        pairs_file_path = directory_path / "pairs"
        print(self.pairs)
        with open(pairs_file_path, "w") as pairs_file:
            for pair in self.pairs:
                pairs_file.write("{0}->{1}\n".format(self.pairs[pair], pair))

class LinearStrategy(GenericStrategy):
    """
    Iterates over a Git repository.

    Each iteration checks out the first parent of the current commit
    and returns the SHA of the parent.
    """
    def __init__(self, repo_path, start, finish, only_paths=None):
        super(LinearStrategy, self).__init__(repo_path, start, finish, only_paths)

    def __next__(self):
        if self.last == self.finish:
            raise StopIteration

        if self.last is None:
            candidate = self.repo.commit(self.start)
        else:
            candidate = self.repo.commit(self.last).parents[0]

        skipped = 0
        while not self.is_included(candidate):
            skipped += 1
            candidate = candidate.parents[0]

        if skipped:
            logging.debug("Skipped %d commits before commit '%s'", skipped, candidate.hexsha)

        self.repo_direct.checkout(candidate.hexsha)
        self.last = candidate.hexsha
        return self.last

STRATEGIES = {"linear": LinearStrategy, "pairs": PairStrategy}

def select_strategy(identifier):
    return STRATEGIES[identifier]
