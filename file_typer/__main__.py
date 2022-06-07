"""dsfafas
"""
import argparse
import re
from pathlib import Path

import magic
from tqdm import tqdm

from file_typer import VERSION, argutils, type_table

table = type_table.TABLE

VERSION = '0.0.10'


def parse_arguments():
    """_summary_

    Returns:
        _type_: _description_
    """
    parser = argparse.ArgumentParser(
        description='Add extension to files without-it',
        epilog="""
        - Created by Marcos Peron (mperon@outlook.com)
        [MIT License]
        """
    )
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s '+VERSION)
    # ignores files or directories
    parser.add_argument('-D',
                        '--dry-run',
                        action='store_true',
                        default=False,
                        help='Show what will be done. If set, just print will occur, no renaming')
    parser.add_argument('-C',
                        '--check',
                        action='store_true',
                        default=False,
                        help='Show what will be done. If set, just print will occur, no renaming')
    parser.add_argument('-P',
                        '--playlist',
                        action='store',
                        help='Creates a playlist filtering these mimetypes')

    parser.add_argument('FILE',
                        nargs='+',
                        type=argutils.path_exists,
                        help='An directory or file to process.')
    # process and return
    config = vars(parser.parse_args())
    config["action"] = execute_file
    config["mimes"] = set()
    config["suffix_table"] = set()
    config["ignore_table"] = set()
    # separe playlist as list
    if config.get('playlist', None):
        config['playlist'] = [re.compile(
            pl) for pl in config['playlist'].split(',') if pl]
        config["action"] = execute_playlist
    if not config.get("current_dir", None):
        config["current_dir"] = Path('.')
    if not config.get("pl_filename", None):
        config["pl_filename"] = 'playlist.m3u'

    return config


def main():
    """_summary_
    """
    config = parse_arguments()
    try:
        for path in config.get('FILE', []):
            path = Path(path)
            if path.is_dir():
                execute_dir(config, path)
            elif path.is_file():
                config["action"](config, path, None)
        # print mimes
        print("Unknown Mime Types:")
        for mime in sorted(config["mimes"]):
            print(f'"{mime}": ".",')
    except Exception:  # pylint: disable=broad-except
        if config.get('pl_file', None):
            config['pl_file'].close()


def execute_dir(config, directory):
    """_summary_

    Args:
        config (_type_): _description_
    """
    print(f"Calculating files on folder: {directory}")
    config["current_dir"] = directory
    list_of = list(Path(directory).glob('**/*'))
    total = len(list_of)
    p_bar = tqdm(list_of, mininterval=3, total=total, desc="Processando")
    for path in p_bar:
        config["action"](config, path, p_bar)


def execute_playlist(config, p_file, p_bar):
    # pylint: disable=unused-argument
    """_summary_

    Args:
        config (_type_): _description_
        p_file (_type_): _description_
        p_bar (_type_): _description_
    """
    if p_file.is_dir():
        #print("[PASS] File is directory..")
        return
    # try search on saved suffix table
    if len(p_file.suffixes) > 0:
        f_ext = p_file.suffix
        if f_ext in config["suffix_table"]:
            playlist_save_to(config, p_file)
            return True
        if f_ext in config["ignore_table"]:
            return

    mime = magic.from_file(p_file, mime=True)
    if any(pt.match(mime) for pt in config['playlist']):
        config["suffix_table"].add(p_file.suffix)
        playlist_save_to(config, p_file)
        return True
    else:
        config["ignore_table"].add(p_file.suffix)


def playlist_save_to(config, p_file):
    """_summary_

    Args:
        config (_type_): _description_
        p_file (_type_): _description_
    """

    if not config.get('pl_file', None):
        config['pl_file'] = open(config["current_dir"] / config['pl_filename'],
                                 'w', encoding='utf8')
    config['pl_file'].write(
        str(p_file.relative_to(config["current_dir"]))+'\n')


def execute_file(config, p_file, p_bar):
    """_summary_

    Args:
        config (_type_): _description_
        dir (_type_): _description_
    """
    if p_file.is_dir():
        #print("[PASS] File is directory..")
        return
    # check extension
    if len(p_file.suffixes) > 0:
        #print(f"[PASS] File already has extension: {p_file.name}")
        return
    # processing file
    mime = magic.from_file(p_file, mime=True)
    ext = table.get(mime, '')
    if len(ext) > 1:
        new_p = p_file.with_suffix(ext)
        if config.get('check', False):
            return
        if config.get('dry_run', False):
            if not p_bar:
                print(f"[CHG] Renaming to {new_p.name} [DRY]")
        else:
            if not p_bar:
                print(f"[CHG] Renaming to {new_p.name}")
            p_file.rename(new_p)
    else:
        if not p_bar:
            print(f"[IGN] Mime {mime} not found in hash table...")
        config["mimes"].add(mime)


if __name__ == "__main__":
    main()
