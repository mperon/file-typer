# File Typer

Append extension in files without-it, based on mimetypes
Some files comes without any extension and windows comply
about it! Because of that, several tools, including Windows Explorer cannot
show the users the file preview, and cannot open-it.

This tool allows the user pass an directory/file and traverse-it, renaming
files, putting extension of known table into-it, based on mimetypes

## Requirements

* You must install Python 3.8 ou superior.
* Works only on Linux or MacOS

## Installation

*file-typer* can be installed using pip:

    python3 -m pip install -U file-typer

If you want to run the latest version of the code, you can install from git:

    python3 -m pip install -U git+https://github.com/mperon/file-typer.git

## Usage

The applications uses command line arguments to interact with the user. To see
all the options, execute:

`file-typer --help`

To process a folder, run with this command:

`file-typer /path/to/folder -o /path/to/output`
