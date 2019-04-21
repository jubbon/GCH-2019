#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import contextlib
import errno


@contextlib.contextmanager
def directory_exists(path):
    """ Менеджер контекста для создания каталога
    """
    try:
        try:
            if not os.path.isdir(path):
                os.makedirs(path)
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise
        yield
    finally:
        pass


@contextlib.contextmanager
def working_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.

    """
    prev_cwd = os.getcwd()
    full_path = os.path.abspath(path)
    with directory_exists(full_path):
        os.chdir(full_path)
        try:
            yield full_path
        finally:
            os.chdir(prev_cwd)
