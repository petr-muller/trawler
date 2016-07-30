'''
Created on Jul 30, 2016

@author: Petr Muller
'''
import subprocess
import shlex
import path

class Executor(object):
    """
    This module implements actions over project repositories.
    """

    def __init__(self, repo_path, compile_recipe, test_recipe, clean_recipe):
        self.repo_path = path.Path(repo_path)
        self.compile_recipe = compile_recipe
        self.test_recipe = test_recipe
        self.clean_recipe = clean_recipe

    @staticmethod
    def _run_recipe(recipe):
        for item in recipe:
            to_run = shlex.split(item)
            subprocess.check_call(to_run)

    def compile(self):
        """
        Execute a recipe to compile the software project.
        """
        with self.repo_path:
            Executor._run_recipe(self.compile_recipe)

    def test(self):
        """
        Execute a recipe to run a projects testsuite.
        """
        with self.repo_path:
            Executor._run_recipe(self.test_recipe)

    def clean(self):
        """
        Execute a recipe to clean the projects build state.
        """
        with self.repo_path:
            Executor._run_recipe(self.clean_recipe)
