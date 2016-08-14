'''
Created on Jul 30, 2016

@author: Petr Muller
'''
import subprocess
import shlex
from pathlib import Path

class Executor(object):
    """
    This module implements actions over project repositories.
    """

    def __init__(self, repo_path, compile_recipe, test_recipe, clean_recipe):
        self.repo_path = Path(repo_path)
        self.compile_recipe = compile_recipe
        self.test_recipe = test_recipe
        self.clean_recipe = clean_recipe

    @staticmethod
    def _run_recipe(recipe, output=subprocess.DEVNULL, check=True):
        for item in recipe:
            to_run = shlex.split(item)
            subprocess.run(to_run, stdout=output, stderr=subprocess.STDOUT, check=check)

    def compile(self, output_file_path):
        """
        Execute a recipe to compile the software project.
        """
        with open(output_file_path, "w") as output_file:
            with self.repo_path:
                Executor._run_recipe(self.compile_recipe, output=output_file, check=True)

    def test(self, output_file_path):
        """
        Execute a recipe to run a projects testsuite.
        """
        with open(output_file_path, "w") as output_file:
            with self.repo_path:
                Executor._run_recipe(self.test_recipe, output=output_file, check=False)

    def clean(self):
        """
        Execute a recipe to clean the projects build state.
        """
        with self.repo_path:
            Executor._run_recipe(self.clean_recipe, check=False)
