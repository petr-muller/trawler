'''
Created on Jul 30, 2016

@author: Petr Muller
'''
import configparser
import datetime
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

        self.recipe = configparser.ConfigParser()
        self.recipe.read(recipe_file)

        self.output_directory = None

    def _get_recipes(self):

        compile_recipe = self.recipe["recipes"]["compile"].split(';')
        test_recipe = self.recipe["recipes"]["test"].split(';')
        clean_recipe = self.recipe["recipes"]["clean"].split(";")

        return (compile_recipe, test_recipe, clean_recipe)

    def prepare_output_directory(self):
        """
        Prepares an output directory for this crawling run.
        """
        output_dir_name = "{0}-{1}".format(self.recipe["metadata"]["name"],
                                           datetime.datetime.now().isoformat())
        output_dir = os.getcwd() / Path(output_dir_name)

        if output_dir.exists():
            logging.debug("Output directory '%s' exists: removing", output_dir)
            output_dir.rmtree()
        output_dir.makedirs()

        logging.debug("Setting output directory: %s", output_dir)
        self.output_directory = output_dir

    def run(self):
        """
        Starts crawling.
        """

        compile_recipe, test_recipe, clean_recipe = self._get_recipes()
        repository_executor = Executor(self.repo_path, compile_recipe, test_recipe, clean_recipe)

        iterator = GitRepoIterator(self.repo_path, self.top, self.bottom, only_paths=self.recipe["repository"]["filter"])

        self.prepare_output_directory()

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
            output_file_path = self.output_directory / output_filename
            test_start = timeit.default_timer()
            repository_executor.test(output_file_path)
            test_end = timeit.default_timer()
            logging.info("Testing revision:    %s: finished (%d seconds)", revision,
                         test_end - test_start)
            counter += 1
