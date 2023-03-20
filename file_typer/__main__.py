"""dsfafas
"""
import argparse
from pathlib import Path

from file_typer import argutils, type_table
from file_typer.impl import AddExtensionAction, ProgressBarAction, Walker

table = type_table.TABLE

VERSION = '1.0.16'


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
    parser.add_argument('-U',
                        '--dry-run',
                        action='store_true',
                        default=False,
                        help='Show what will be done. DO NOTHING!')
    parser.add_argument('-f',
                        '--force',
                        action='store_true',
                        default=False,
                        help='Overwrite existing file\'s.')
    parser.add_argument('-X',
                        '--no-progress',
                        action='store_true',
                        default=False,
                        help='Disables progress bar show, and print each rename.')
    parser.add_argument('-C',
                        '--no-copy',
                        action='store_true',
                        default=False,
                        help='Just copy renamed files, not the entire structure')
    parser.add_argument('-o',
                        '--output',
                        action='store',
                        type=argutils.is_valid_dir,
                        default=Path.cwd(),
                        help='Directory to output the renamed files.')
    parser.add_argument('FILE',
                        nargs='+',
                        type=argutils.path_exists,
                        help='An directory or file to process.')
    # process and return
    config = vars(parser.parse_args())
    if config.get('dry_run', False):
        config['no_progress'] = True
    config['output'] = Path(config.get('output', Path.cwd()))
    return config


def main():
    """_summary_
    """
    config = parse_arguments()
    output = config['output']
    action = AddExtensionAction()
    for path in config.get('FILE', []):
        path = Path(path)
        if Path(output) == Path(path):
            print("ERROR: Output is the same folder that input! Skipping.")
            continue
        walker = Walker.create(path, config)
        if not config["no_progress"]:
            action = ProgressBarAction(action, path)
        action.start()
        walker.walk(action)
        action.done()


if __name__ == "__main__":
    main()
