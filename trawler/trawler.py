'''
Created on Jul 30, 2016

@author: Petr Muller
'''
import configparser
import logging
import os
import timeit

from path import Path

from trawler.executor import Executor
from trawler.repo_iterator import GitRepoIterator


class Trawler(object):
    """
    Crawls a Git repository, obtaining test result artifacts for each revision.
    """
    def __init__(self, repository_path, recipe_file, top_revision, bottom_revision):
        self.repo_path = repository_path
        self.top = top_revision
        self.bottom = bottom_revision
        self.recipe_file = recipe_file

    def _get_recipes(self):
        parser = configparser.ConfigParser()
        parser.read(self.recipe_file)

        compile_recipe = parser["recipes"]["compile"].split(';')
        test_recipe = parser["recipes"]["test"].split(';')
        clean_recipe = parser["recipes"]["clean"].split(";")

        return (compile_recipe, test_recipe, clean_recipe)


    def run(self):
        """
        Starts crawling.
        """

        compile_recipe, test_recipe, clean_recipe = self._get_recipes()
        repository_executor = Executor(self.repo_path, compile_recipe, test_recipe, clean_recipe)

        iterator = GitRepoIterator(self.repo_path, self.top, self.bottom)

        output_dir = os.getcwd() / Path("output")
        if output_dir.exists():
            output_dir.rmtree()
        output_dir.makedirs()

        counter = 1
        for revision in iterator:
            logging.info("Processing revision: %s", revision)
            logging.info("Compiling revision:  %s", revision)
            compile_start = timeit.default_timer()
            repository_executor.compile()
            compile_end = timeit.default_timer()
            logging.info("Compiling revision:  %s: OK (%d seconds)", revision,
                         compile_end - compile_start)

            logging.info("Testing revision:    %s", revision)
            output_filename = "{0:04d}-{1}".format(counter, revision)
            output_file_path = output_dir / output_filename
            test_start = timeit.default_timer()
            repository_executor.test(output_file_path)
            test_end = timeit.default_timer()
            logging.info("Testing revision:    %s: finished (%d seconds)", revision,
                         test_end - test_start)
            counter += 1
