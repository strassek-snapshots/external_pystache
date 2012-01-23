# coding: utf-8

"""
This module provides a Locator class for finding template files.

"""

import os
import re
import sys


DEFAULT_EXTENSION = 'mustache'


class Locator(object):

    def __init__(self, extension=None):
        """
        Construct a template locator.

        Arguments:

          extension: the template file extension.  Defaults to "mustache".
            Pass False for no extension (i.e. extensionless template files).

        """
        if extension is None:
            extension = DEFAULT_EXTENSION

        self.template_extension = extension

    def _find_path(self, file_name, search_dirs):
        """
        Search for the given file, and return the path.

        Returns None if the file is not found.

        """
        for dir_path in search_dirs:
            file_path = os.path.join(dir_path, file_name)
            if os.path.exists(file_path):
                return file_path

        return None

    def get_object_directory(self, obj):
        """
        Return the directory containing an object's defining class.

        Returns None if there is no such directory, for example if the
        class was defined in an interactive Python session, or in a
        doctest that appears in a text file (rather than a Python file).

        """
        if not hasattr(obj, '__module__'):
            return None

        module = sys.modules[obj.__module__]

        if not hasattr(module, '__file__'):
            # TODO: add a unit test for this case.
            return None

        path = module.__file__

        return os.path.dirname(path)

    def make_file_name(self, template_name):
        file_name = template_name
        if self.template_extension is not False:
            file_name += os.path.extsep + self.template_extension

        return file_name

    def make_template_name(self, obj):
        """
        Return the canonical template name for an object instance.

        This method converts Python-style class names (PEP 8's recommended
        CamelCase, aka CapWords) to lower_case_with_underscords.  Here
        is an example with code:

        >>> class HelloWorld(object):
        ...     pass
        >>> hi = HelloWorld()
        >>>
        >>> locator = Locator()
        >>> locator.make_template_name(hi)
        'hello_world'

        """
        template_name = obj.__class__.__name__

        def repl(match):
            return '_' + match.group(0).lower()

        return re.sub('[A-Z]', repl, template_name)[1:]

    def _find_path_by_file_name(self, search_dirs, file_name):
        """
        Return the path to a template with the given file name.

        """
        path = self._find_path(file_name, search_dirs)

        if path is None:
            # TODO: we should probably raise an exception of our own type.
            raise IOError('Template file %s not found in directories: %s' %
                          (repr(file_name), repr(search_dirs)))

        return path

    def find_path_by_name(self, search_dirs, template_name):
        """
        Return the path to a template with the given name.

        """
        file_name = self.make_file_name(template_name)

        return self._find_path_by_file_name(search_dirs, file_name)

    def find_path_by_object(self, search_dirs, obj, file_name=None):
        """
        Return the path to a template associated with the given object.

        """
        if file_name is None:
            # TODO: should we define a make_file_name() method?
            template_name = self.make_template_name(obj)
            file_name = self.make_file_name(template_name)

        dir_path = self.get_object_directory(obj)

        if dir_path is not None:
            search_dirs = [dir_path] + search_dirs

        path = self._find_path_by_file_name(search_dirs, file_name)

        return path
