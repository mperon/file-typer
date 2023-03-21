#!/usr/bin/env python3
"""Decode record information from FileListInfo
"""
import io
import json
import os
import pathlib
import plistlib
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

import magic
from tqdm import tqdm

from file_typer import type_table

table = type_table.TABLE


SEEK_DATA = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com\
/DTDs/PropertyList-1.0.dtd">',
    '<plist version="1.0">',
]
FILEINFO_NAME = "FileInfoList"
KEYBAG_NAME = "keyBag"
APPLY_REGEX = (
    (re.compile(r"(\r\n|\n)"), " "),  # remove all newlines
    (re.compile(r"\}\](\s+)?\["), "},"),  # remove all }][
    (re.compile(r"\t+"), " "),  # replaces tabs with spaces
)


class AppleInfo:
    """_summary_"""

    SEARCH_NAME = "NO.txt"

    def real_id(self, fid):
        """_summary_

        Args:
            fid (_type_): _description_

        Returns:
            _type_: _description_
        """
        real = str(fid).replace("__", "/")
        real = real.replace("_", ":")
        return real

    @classmethod
    def search_up(cls, path: Path):
        """_summary_

        Args:
            path (Path): _description_

        Returns:
            _type_: _description_
        """
        for parent in path.parents:
            fli_p = parent / cls.SEARCH_NAME
            if fli_p.exists():
                return cls(None, parent)
        return None


class FileInfoList(AppleInfo):
    """_summary_"""

    SEARCH_NAME = f"{FILEINFO_NAME}.zip"

    def __init__(self, parent=None, path=None) -> None:
        super().__init__()
        self.parent = parent
        self.data = {}
        if path:
            self.load(path)

    def load(self, path):
        """_summary_

        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        path = Path(path)
        if path.is_dir():
            # load default
            zip_file = path / self.SEARCH_NAME
            if zip_file.exists():
                with ZipFile(zip_file) as zip_file:
                    with io.TextIOWrapper(
                        zip_file.open(f"{FILEINFO_NAME}.txt", mode="r"), encoding="utf-8"
                    ) as file:
                        lines = file.readlines()
                        self.from_text(lines)

    def from_text(self, text):
        """_summary_

        Args:
            text (_type_): _description_

        Returns:
            _type_: _description_
        """
        start = 0
        if not isinstance(text, list):
            return self.from_text(re.split(r"(\r\n|\n)", text))
        for lno, line in enumerate(text):
            if str(line).strip().startswith(r'[{"id":'):
                start = lno
                break
        json_data = self._load_lines(text[start:])
        if "records" in json_data:
            self.data = self._build(json_data["records"])
        return self.data

    def _build(self, json_data):
        registry = {}
        for item in json_data:
            item["real_id"] = self.real_id(item["id"])
            registry[item["real_id"]] = item
        return registry

    def has(self, fid):
        """_summary_

        Args:
            fid (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.real_id(fid) in self.data

    def device_id(self, fid):
        """_summary_

        Args:
            fid (_type_): _description_

        Returns:
            _type_: _description_
        """
        real_id = self.real_id(fid)
        id_parts = real_id.split(":")
        return id_parts[1]

    def get_real_name(self, fid):
        """_summary_

        Args:
            fid (_type_): _description_

        Returns:
            _type_: _description_
        """
        item = self.data.get(self.real_id(fid), None)
        if item:
            plist_xml = item["fields"]["encryptedAttributes"]
            plist_bin = bytes(plist_xml, "utf-8")
            plist = plistlib.loads(plist_bin)
            return plist["relativePath"]
        if self.parent:
            return self.parent.get_real_name(fid)
        return ""

    def _load_lines(self, lines):
        contents = " ".join(lines)
        # process text file
        for seek in SEEK_DATA:
            contents = contents.replace(seek, seek.replace('"', '\\"'))
        for regx, sub in APPLY_REGEX:
            contents = regx.sub(sub, contents)
        contents = '{"records": ' + contents + "}"
        return json.loads(contents)


class Action:
    """_summary_"""

    def start(self):
        """_summary_"""

    def execute(self, ctx, p_file):
        """_summary_

        Args:
            ctx (_type_): _description_
            p_file (_type_): _description_
        """

    def done(self):
        """_summary_

        Raises:
            ValueError: _description_
            ValueError: _description_

        Returns:
            _type_: _description_
        """


class ProgressBarAction(Action):
    """_summary_

    Args:
        Action (_type_): _description_
    """

    def __init__(self, action, path=None, total=None) -> None:
        self.action = action
        if path:
            self.total = self.count_files(path)
        if total:
            self.total = total
        self.p_bar = None

    def start(self):
        self.p_bar = tqdm(total=self.total, unit="f", desc="Processando")

    def count_files(self, path):
        """_summary_

        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        return sum(len(files) for _, _, files in os.walk(str(Path(path))))

    def execute(self, ctx, p_file):
        """_summary_

        Args:
            ctx (_type_): _description_
            p_file (_type_): _description_
        """
        self.p_bar.update()
        self.action.execute(ctx, p_file)

    def done(self):
        self.p_bar.close()


class AddExtensionAction(Action):
    """_summary_

    Args:
        Action (_type_): _description_
    """

    def __init__(self) -> None:
        self.unknown = set()

    def execute(self, ctx, p_file):
        if p_file.is_dir():
            # print("[PASS] File is directory..")
            return
        # check file has already extension
        if len(p_file.suffixes) > 0:
            if ctx.config["only_changed"]:
                return
            ctx.copy_file(p_file, p_file.name)
            return

        # check if has a info table
        real_path = ctx.info.get_real_name(p_file.name)
        if real_path:
            p_file_to = real_path
            ctx.copy_file(p_file, p_file_to)
        else:
            try:
                mime = magic.from_file(str(p_file), mime=True)
            except Exception as _:
                print(f"Impossible to detect mime for {p_file}. Copying..")
                ctx.copy_file(p_file, p_file.name)
                return
            ext = table.get(mime, "")
            if ext:
                p_file_to = p_file.with_suffix(ext).name
                ctx.copy_file(p_file, p_file_to, relative=False)
            else:
                self.unknown.add(mime)


class Walker:
    """_summary_"""

    def __init__(self, parent, path, config) -> None:
        self.path = path
        self._config = config
        self.parent = None
        if parent:
            self.info = FileInfoList(parent.info, path)
            self.parent = parent
        else:
            # try to search up
            self.info = FileInfoList(FileInfoList.search_up(path), path)

    def directory_name(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if self.parent is not None:
            parent_name = self.parent.directory_name()
            if parent_name:
                return self.parent.directory_name() + pathlib.os.sep + self.path.name
            return self.path.name
        return ""

    def copy_file(self, p_file_from, p_file_to, relative=True):
        """_summary_

        Args:
            p_file_from (_type_): _description_
            p_file_to (_type_): _description_
        """
        p_base_dir = Path(self.config.get("output", None))
        if p_base_dir is None:
            p_base_dir = Path.cwd()

        if relative:
            p_destination = Path(p_base_dir) / self.directory_name() / p_file_to
        else:
            p_destination = p_base_dir / p_file_to

        if p_destination == p_file_from:
            return

        p_destination = normalize_path(p_destination)

        # check dry-run
        if self.config.get("dry_run", False):
            print(f"From: {p_file_from} -> {p_destination}. DRY-RUN!")
            if self.config.get("delete", False):
                print(f"Delete {p_file_from}")
            return

        # check if destination exists (and force is set!)
        if p_destination.exists():
            # check is force
            if not self.config.get("force", False):
                if self.config.get("debug", False):
                    print(
                        f"COPY Failed! Destination file {p_destination} already exists! Skipping.."
                    )
                return

        # print file copy
        if self.config.get("no_progress", False):
            print("From: {p_file_from} -> {p_destination}.", end="")

        # ensures that directory exists
        if not Path(p_destination).parent.exists():
            Path(p_destination).parent.mkdir(exist_ok=True, parents=True)

        # copy file to new location
        shutil.copy(p_file_from, p_destination)
        if self.config.get("delete", False):
            p_file_from.unlink()
        # prints done!
        if self.config.get("no_progress", False):
            print("Done!")

    @property
    def config(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if self._config:
            return self._config
        if self.parent:
            return self.parent.config
        return {}

    def execute(self, action, path):
        """_summary_

        Args:
            action (_type_): _description_
            path (_type_): _description_
        """
        action.execute(self, path)

    @staticmethod
    def create(path, config):
        """_summary_

        Args:
            path (_type_): _description_
            config (_type_): _description_

        Returns:
            _type_: _description_
        """
        if Path(path).is_dir():
            return DirectoryWalker(None, path, config)
        return FileWalker(None, path, config)


class FileWalker(Walker):
    """_summary_

    Args:
        Walker (_type_): _description_
    """

    def __init__(self, parent, path, config) -> None:
        if not Path(path).is_file():
            raise ValueError("this class expects an file")
        self.file_path = path
        path = path.parent
        super().__init__(parent, path, config)

    def walk(self, action):
        """_summary_

        Args:
            action (_type_): _description_
        """
        action.execute(self, Path(self.file_path))


class DirectoryWalker(Walker):
    """_summary_

    Args:
        Walker (_type_): _description_
    """

    def __init__(self, parent, path, config) -> None:
        if not Path(path).is_dir():
            raise ValueError("this class expects an directory")
        super().__init__(parent, path, config)
        self._device_name = None

    def walk(self, action):
        """_summary_

        Args:
            action (_type_): _description_
        """
        for child in self.path.iterdir():
            if child.is_dir():
                dir_walker = DirectoryWalker(self, child, self._config)
                dir_walker.walk(action)
            else:
                self.execute(action, child)


def normalize_path(path):
    """Normalize pathnames"""
    return Path(re.sub(r'[*?"<>|]', "_", str(path)))
