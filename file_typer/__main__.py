"""dsfafas
"""
import argparse
from pathlib import Path

import magic
from file_typer import VERSION, argutils, type_table

table = type_table.TABLE



def parse_arguments():
    """_summary_

    Returns:
        _type_: _description_
    """
    parser = argparse.ArgumentParser(
        prog='typer',
        description='Add extension to files without-it')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s '+VERSION)
    # ignores files or directories
    parser.add_argument('-D',
                        '--dry-run',
                        action='store_true',
                        default=False,
                        help='Show what will be done. If set, just print will occur, no renaming')

    parser.add_argument('FILE',
                        nargs='+',
                        type=argutils.path_exists,
                        help='An directory or file to process.')
    # process and return
    config = vars(parser.parse_args())
    config["mimes"] = set()
    return config

def main():
    """_summary_
    """
    config = parse_arguments()
    for path in config.get('FILE', []):
        path = Path(path)
        if path.is_dir():
            execute_dir(config, path)
        elif path.is_file():
            execute_file(config, path)
    # print mimes
    print("Mime Types:")
    for mime in sorted(config["mimes"]):
        print(f"\"{mime}\": \".\",")


def execute_dir(config, directory):
    """_summary_

    Args:
        config (_type_): _description_
    """
    for path in Path(directory).glob('**/*'):
        execute_file(config, path)

def execute_file(config, p_file):
    """_summary_

    Args:
        config (_type_): _description_
        dir (_type_): _description_
    """
    if p_file.is_dir():
        #print("[PASS] File is directory..")
        return
    #check extension
    if len(p_file.suffixes) > 0:
        #print(f"[PASS] File already has extension: {p_file.name}")
        return
    #processing file
    mime = magic.from_file(p_file, mime=True)
    ext = table.get(mime, None)
    if len(ext) > 1:
        new_p=p_file.with_suffix(ext)

        if config.get('dry_run', False):
            print(f"[CHG] Renaming to {new_p.name} [DRY]")
        else:
            print(f"[CHG] Renaming to {new_p.name}")
            p_file.rename(new_p)

    else:
        print(f"[IGN] Mime {mime} not found in hash table...")
        config["mimes"].add(mime)

if __name__ == "__main__":
    main()
