# coding: utf-8

"""
Allows all tests to be run.

This module is for our test console script.

"""

import os
import sys
import unittest


UNITTEST_FILE_PREFIX = "test_"

# TODO: enhance this to work with doctests (instead of using the load_tests
#   protocol), etc.
class Tester(object):

    """
    Discovers and runs unit tests.

    """

    def _find_unittest_files(self, package_dir):
        """
        Return a list of paths to all unit-test files in the given package directory.

        """
        unittest_paths = []  # Return value.

        def is_unittest(file_name):
            return file_name.startswith(UNITTEST_FILE_PREFIX) and file_name.endswith('.py')

        # os.walk() is new in Python 2.3
        #   http://docs.python.org/library/os.html#os.walk
        for dir_path, dir_names, file_names in os.walk(package_dir):
            file_names = filter(is_unittest, file_names)

            for file_name in file_names:
                unittest_path = os.path.join(dir_path, file_name)
                unittest_paths.append(unittest_path)

        return unittest_paths

    def _modules_from_paths(self, package_dir, paths):
        """
        Return a list of fully-qualified module names given paths.

        """
        package_dir = os.path.abspath(package_dir)
        package_name = os.path.split(package_dir)[1]

        prefix_length = len(package_dir)

        module_names = []
        for path in paths:
            path = os.path.abspath(path)  # for example <path_to_package>/subpackage/module.py
            rel_path = path[prefix_length:]  # for example /subpackage/module.py
            rel_path = os.path.splitext(rel_path)[0]  # for example /subpackage/module

            parts = []
            while True:
                (rel_path, tail) = os.path.split(rel_path)
                if not tail:
                    break
                parts.insert(0, tail)
            # We now have, for example, ['subpackage', 'module'].
            parts.insert(0, package_name)
            module = ".".join(parts)
            module_names.append(module)

        return module_names

    # TODO: consider replacing the package argument with a package_dir argument.
    def run_tests(self, package, sys_argv):
        """
        Run all unit tests inside the given package.

        Arguments:

          package: a module instance corresponding to the package.

          sys_argv: a reference to sys.argv.

        """
        if len(sys_argv) > 1 and not sys_argv[-1].startswith("-"):
            # Then explicit modules or test names were provided, which
            # the unittest module is equipped to handle.
            unittest.main(argv=sys_argv, module=None)
            # No need to return since unitttest.main() exits.

        # Otherwise, auto-detect all unit tests.

        package_dir = os.path.dirname(package.__file__)
        unittest_paths = self._find_unittest_files(package_dir)

        modules = self._modules_from_paths(package_dir, unittest_paths)
        modules.sort()

        # This is a sanity check to ensure that the unit-test discovery
        # methods are working.
        if len(modules) < 1:
            raise Exception("No unit-test modules found.")

        sys_argv.extend(modules)

        # We pass None for the module because we do not want the unittest
        # module to resolve module names relative to a given module.
        # (This would require importing all of the unittest modules from
        # this module.)  See the loadTestsFromName() method of the
        # unittest.TestLoader class for more details on this parameter.
        unittest.main(argv=sys_argv, module=None)
