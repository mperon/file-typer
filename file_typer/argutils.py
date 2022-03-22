"""Argutils

this do some stuff
"""
# vim: ts=4 sw=4 et
import argparse
import os
from urllib.parse import urlparse


def expand_path(path):
    """_summary_

    Args:
        path (_type_): _description_

    Returns:
        _type_: _description_
    """
    return os.path.abspath(os.path.expanduser(
        os.path.expandvars(path)))


def is_dir(dirname):
    """_summary_

    Args:
        dirname (_type_): _description_

    Raises:
        argparse.ArgumentTypeError: _description_

    Returns:
        _type_: _description_
    """
    dirname = expand_path(dirname)
    if not os.path.isdir(dirname):
        msg = f"{dirname} is not a directory"
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


def can_create_dir(path):
    """_summary_

    Args:
        path (_type_): _description_

    Returns:
        _type_: _description_
    """
    parts = os.path.split(path)
    if os.path.exists(parts[0]):
        return True
    else:
        if not parts[1] == '':
            return can_create_dir(parts[0])
        else:
            return False


def is_searchable_file(path):
    """_summary_

    Args:
        path (_type_): _description_

    Raises:
        argparse.ArgumentTypeError: _description_

    Returns:
        _type_: _description_
    """
    path = expand_path(path)
    if os.path.isfile(path) and is_readable(path):
        return path
    raise argparse.ArgumentTypeError(
        f"Config file {path} doesnt exists!")


def path_exists(path):
    """_summary_

    Args:
        path (_type_): _description_

    Raises:
        argparse.ArgumentTypeError: _description_

    Returns:
        _type_: _description_
    """
    path = expand_path(path)
    if os.path.exists(path):
        return path
    raise argparse.ArgumentTypeError(
        f"{path} is not a valid file/dir!")


def is_valid_file(path):
    """_summary_

    Args:
        path (_type_): _description_

    Raises:
        argparse.ArgumentTypeError: _description_

    Returns:
        _type_: _description_
    """
    path = expand_path(path)
    if os.path.isfile(path) and is_readable(path):
        return path
    raise argparse.ArgumentTypeError(
        f"Config file {path} doesnt exists!")


def is_valid_dir(path):
    """_summary_

    Args:
        path (_type_): _description_

    Raises:
        argparse.ArgumentTypeError: _description_

    Returns:
        _type_: _description_
    """
    path = expand_path(path)
    if is_dir(path):
        return path
    else:
        # is not a directory, verify file
        if not os.path.exists(path):
            # path dont exist, check if can be create
            if can_create_dir(path):
                return path
    raise argparse.ArgumentTypeError(
        f"{path} is not a valid directory path")


def is_url(url):
    """_summary_

    Args:
        url (_type_): _description_

    Raises:
        argparse.ArgumentTypeError: _description_

    Returns:
        _type_: _description_
    """
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return url
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(f"{url} is not a valid url")


def is_executable(path):
    """_summary_

    Args:
        path (_type_): _description_

    Returns:
        _type_: _description_
    """
    return os.access(path, os.X_OK)


def is_readable(path):
    """_summary_

    Args:
        path (_type_): _description_

    Returns:
        _type_: _description_
    """
    return os.access(path, os.R_OK)


class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(
            os.path.expanduser(values)))


class FileFinder:
    """_summary_

    Returns:
        _type_: _description_
    """
    COMMENTS = ('#', ";", "//")

    def __init__(self, fname):
        self.fname = fname
        self._load_paths()

    def _load_paths(self):
        paths = []
        self.fname = expand_path(self.fname)
        if os.path.isfile(self.fname) and is_readable(self.fname):
            with open(self.fname, 'utf-8') as fp:
                for line in fp:
                    if line.strip() == "":
                        continue
                    elif any(map(lambda x: line.strip().startswith(x), FileFinder.COMMENTS)):
                        continue  # is a comment, ignore line
                    else:
                        path = os.path.abspath(os.path.expanduser(
                            os.path.expandvars(line.strip())))
                        if os.path.isdir(path):
                            paths.append(path)
        self.paths = tuple(paths)

    def file_exists(self, path):
        """_summary_

        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.get_file_path(path) is not False

    def get_file_path(self, path):
        """_summary_

        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        if os.path.isabs(path):
            if os.path.isfile(path) and is_readable(path):
                return path
        for path_prefix in self.paths:
            fullpath = os.path.join(path_prefix, path)
            if os.path.isfile(fullpath) and is_readable(fullpath):
                return fullpath
        return False
