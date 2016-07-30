'''
Created on Jul 30, 2016

@author: Petr Muller
'''

class Trawler(object):
    """
    Crawls a Git repository, obtaining test result artifacts for each revision.
    """
    def __init__(self, repository_path, top_revision, bottom_revision):
        self.repo_path = repository_path
        self.top = top_revision
        self.bottom = bottom_revision


    def run(self):
        """
        Starts crawling.
        """
        pass
