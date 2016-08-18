'''
Created on Jul 30, 2016

@author: Petr Muller
'''
import configparser
import datetime
import logging
import os
import timeit
import shutil
from typing import Tuple, List

from path import Path

from trawler.executor import Executor
from trawler.repo_iterator import select_strategy


class Trawler(object):
    """
    Crawls a Git repository, obtaining test result artifacts for each revision.
    """
    def __init__(self, repository_path: str, recipe_file: str, top_revision: str,
                 bottom_revision: str, strategy: str) -> None:
        self.repo_path = Path(repository_path)
        self.top = top_revision
        self.bottom = bottom_revision

        self.recipe = configparser.ConfigParser()
        self.recipe.read(recipe_file)

        self.output_directory = None # type: Path

        self.strategy = strategy

    def _get_recipes(self) -> Tuple[List[str], List[str], List[str]]:

        compile_recipe = self.recipe["recipes"]["compile"].split(';')
        test_recipe = self.recipe["recipes"]["test"].split(';')
        clean_recipe = self.recipe["recipes"]["clean"].split(";")

        return (compile_recipe, test_recipe, clean_recipe)

    def prepare_output_directory(self) -> None:
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


    def process_revision(self, repository_executor, iterator, counter, revision):
        """Process a single revision"""

        logging.info("Processing revision: %s", revision)
        logging.info("Compiling revision:  %s", revision)

        output_filename = "{0:04d}-{1}-compile-log".format(counter, revision)
        output_file_path = self.output_directory / output_filename

        compile_start = timeit.default_timer()
        repository_executor.compile(output_file_path)
        output_file_path.remove()
        compile_end = timeit.default_timer()
        logging.info("Compiling revision:  %s: OK (%d seconds)", revision,
                     compile_end - compile_start)

        logging.info("Testing revision:    %s", revision)
        output_filename = "{0:04d}-{1}".format(counter, revision)
        output_file_path = self.output_directory / output_filename
        test_start = timeit.default_timer()
        repository_executor.test(output_file_path)
        if "artifacts" in self.recipe:
            for artifact in self.recipe["artifacts"]:
                artifact_path = self.output_directory / ("{0}-{1}".format(output_file_path,
                                                                          artifact))
                shutil.copyfile(self.repo_path / self.recipe["artifacts"][artifact], artifact_path)

        test_end = timeit.default_timer()
        logging.info("Testing revision:    %s: finished (%d seconds)", revision,
                     test_end - test_start)
        counter += 1
        iterator.write_data(self.output_directory)

    def run(self) -> None:
        """
        Starts crawling.
        """

        compile_recipe, test_recipe, clean_recipe = self._get_recipes()
        repository_executor = Executor(self.repo_path, compile_recipe, test_recipe, clean_recipe)

        strategy = select_strategy(self.strategy)

        iterator = strategy(self.repo_path, self.top, self.bottom,
                            only_paths=self.recipe["repository"]["filter"])

        self.prepare_output_directory()

        counter = 1
        for revision in iterator:
            self.process_revision(repository_executor, iterator, counter, revision)
