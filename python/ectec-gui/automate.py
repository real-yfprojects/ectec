#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""
Automate parts of the development process regarding PyQt5.

Functions
---------
make_pro_file
    Generate and write the .pro project file of the PyQt project.
pyuic5
    Generate the configured from python modules from the .ui form files.
pyrcc5
    Generate the qt resource module from .qrc files.
pylupdate5
    Update the translation files using `pylupdate5`.


files_recursive
    Make a list of files from a list of directories and files.


Notes
-----
This script can be used with `argcomplete` which is a python package providing
bash completion for compatible python programs that use argparse.

More information on argcomplete can be found on
it's `Github page <https://github.com/kislyuk/argcomplete>`_.

***********************************

Created on 2021/07/01 at 20:06:38

Copyright (C) 2021 real-yfprojects (github.com user)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
import argparse
import subprocess
import sys
from pathlib import Path, PurePath
from typing import List, Tuple
from xml.dom import minidom
from xml.etree import ElementTree

try:
    import argcomplete
except ImportError:
    argcomplete = None

VERSION_TUPLE = (1, 0)
VERSION = '.'.join(map(str, VERSION_TUPLE))

# ---- Configuration ---------------------------------------------------------

#: Path to project file relative to this script.
PROJECT_FILE = "project.pro"

#: List of paths to source files or directories relative to this script.
SOURCES = ["src/ectecgui/"]

#: List of temporary directories not to include in sources.
SOURCES_TEMP_DIRS = ["__pycache__"]

#: List of endings for source files.
SOURCE_ENDINGS = [".py", ".pyw"]

#: Generate resource files from a dictionary.
RESOURCES = {"res/breeze.qrc": ('icons/breeze', "res/breeze-icons/icons", '')}

#: Dictionary matching paths to resource files (.qrc)
#: to the directories for or to the path of the generated python modules.
RESOURCE_FILES = {
    "res/ectec.qrc": "src/ectecgui/",
    "res/breeze.qrc": "src/ectecgui"
}

#: The suffix for python modules part of the qt resource system.
RESOURCE_SUFFIX = "_res"

#: Dictionary matching paths to form files (.ui) to generated python modules.
FORMS = {
    "res/server.ui": "src/ectecgui/server/ui_main.py",
    "res/clientConnect.ui": 'src/ectecgui/client/ui_connect.py',
    "res/clientUser.ui": 'src/ectecgui/client/userclient/ui_main.py'
}

#: List of paths for translation files relative to this script.
TRANSLATIONS = ["res/ectecgui.en.ts", "res/ectecgui.de.ts"]

#: The default verbosity.
VERBOSITY = 2

# ---- Helpers ---------------------------------------------------------------


def pwd() -> Path:
    """
    Get the current working directory.

    The current working directory is the directory of this script.

    Returns
    -------
    Path
    """
    return Path(__file__).parent.resolve()


def solve_relative_path(path) -> Path:
    """
    Resolve a path relative to the current working directory.

    The current working directory is obtained from `pwd()`.

    Parameters
    ----------
    path : a type that can be passed to the constructor of `Path`.
        The relative path.

    Returns
    -------
    Path
        The absolute path.
    """
    return Path(pwd(), path).resolve()


def path(path: Path) -> str:
    """Get the string version of a path."""
    return str(path.resolve().relative_to(Path.cwd()))


# ---- Generate .pro File ----------------------------------------------------


def generate_file_list(name: str,
                       elements: list,
                       center: int,
                       line_max: int = 79) -> str:
    """
    Generate the assignment of a list to a variable inside a project file.

    Parameters
    ----------
    name : str
        The name of the variable.
    elements : list
        The list of elements.
    center : int
        The center of the statement where the equalsign is placed.
    line_max : int, optional
        The maximum line length, by default 79.

    Returns
    -------
    str
        The statement that can be written into the project file.
    """
    content = str(name) + " " * (center - len(name)) + '='
    # print(content)

    # Make str list of elements
    line = ''
    first_line = True

    end_of_line = line_max - (center + 1)  # The length for the code lines
    elements = list(elements)
    while elements:
        element = str(elements.pop())
        if len(line) + len(element) > end_of_line:
            if not first_line:
                # new line
                content += ' \\\n'

                # indent line
                content += (center + 1) * ' '

            first_line = False

            # add code of line
            content += line

            line = ''

        line += ' ' + element

    if not first_line:
        # new line
        content += ' \\\n'

        # indent line
        content += (center + 1) * ' '

    first_line = False

    # add code of line
    content += line

    line = ''

    content += '\n'

    return content


def files_recursive(paths: List[Path],
                    dir_filter: List[str] = [],
                    file_endings: List[str] = []) -> List[Path]:
    """
    Make a list of files from a list of directories and files.

    The directories in the list are recursively searched.

    Parameters
    ----------
    paths : List[Path]
        The paths to the directories and files to be included.
    dir_filter : List[str], optional
        A list of directory names to ignore, by default [].
    file_endings : List[str], optional
        A list of file endings that are allowed, by default all are allowed.

    Returns
    -------
    List[Path]
        The files found.
    """
    files: List[Path] = []

    directories_left: List[Path] = []

    for element in paths:
        element = solve_relative_path(element)
        if element.is_dir():
            directories_left.append(element)
        else:
            files.append(element)

    while directories_left:
        dir = directories_left.pop()
        for element in dir.iterdir():
            if element.is_dir() and element.name not in dir_filter:
                directories_left.append(element.resolve())
            elif element.suffix in file_endings:
                files.append(element.resolve())

    return files


def make_pro_file():
    """
    Generate and write the .pro project file of the PyQt project.

    The .pro project file is needed for the `pylupdate5` command.
    """
    content = ""

    if VERBOSITY > 1:
        print("Generating...")

    if VERBOSITY > 2:
        print()

    # Make List of Sources
    source_files = files_recursive(SOURCES, SOURCES_TEMP_DIRS, SOURCE_ENDINGS)

    # Make list of resource files
    resource_files = files_recursive(RESOURCE_FILES)

    # Make list of form files
    form_files = []

    for file in FORMS:
        file = solve_relative_path(file)
        if not file.is_dir():
            form_files.append(file)

    # Make list of translation files
    trans_files = []

    for file in TRANSLATIONS:
        file = solve_relative_path(file)
        if not file.is_dir():
            trans_files.append(file)

    # Make Lists
    names = ['FORMS', 'TRANSLATIONS', 'RESOURCES', 'SOURCES']
    length = max(map(len, names)) + 1

    if VERBOSITY > 3:
        print(source_files)
        print(resource_files)
        print(form_files)
        print(trans_files)
        print()

    content += generate_file_list("SOURCES", source_files, length)
    content += generate_file_list("RESOURCES", resource_files, length)
    content += generate_file_list("FORMS", form_files, length)
    content += generate_file_list("TRANSLATIONS", trans_files, length)

    if VERBOSITY > 2:
        print(content)
        print()

    # write file
    filepath = solve_relative_path(PROJECT_FILE)

    if VERBOSITY > 0:
        print("Writing to", filepath.resolve(), '...')

    with filepath.open('w') as file:
        file.write(content)


# ---- Generate from .ui files -----------------------------------------------


def pyuic5():
    """
    Generate the configured from python modules from the .ui form files.

    """

    if not FORMS:
        if VERBOSITY > 0:
            print("No forms specified.")

        return

    stdout = sys.stdout if VERBOSITY > 3 else subprocess.DEVNULL

    for form, pymod in FORMS.items():
        form_file = solve_relative_path(form)
        pyui_file = solve_relative_path(pymod)
        if not form_file.is_dir() and not pyui_file.is_dir():
            # generate to file
            pyuic5_cmd = [
                "pyuic5",
                path(form_file),
                '-i',
                str(4),
                '--import-from',
                '.',
                '--resource-suffix',
                RESOURCE_SUFFIX,
                "-o",
                path(pyui_file),
            ]
            if VERBOSITY > 3:
                print("Running \"", ' '.join(pyuic5_cmd), '"', sep='')
            if VERBOSITY > 2:
                print("Generating python module for {} to {}.".format(
                    form_file, pyui_file))
            elif VERBOSITY > 1:
                print("Generating python module for {}.".format(form_file))

            subprocess.run(pyuic5_cmd, stdout=stdout, stderr=sys.stderr)


# ---- Generate .qrc files --------------------------------------------------


def get_alias(file: Path, root: Path, alias_prefix: str) -> str:
    relative = file.relative_to(root)

    return str(alias_prefix / relative)


def qrc_prefix(super_element: ElementTree.Element,
               prefix: str) -> ElementTree.SubElement:
    qresource = ElementTree.SubElement(super_element, "qresource",
                                       {'prefix': prefix})
    return qresource


def qrc_file(super_element: ElementTree.Element,
             path: str,
             alias: str = None) -> ElementTree.SubElement:
    attrib = {'alias': alias} if alias else {}
    file = ElementTree.SubElement(super_element, "file", attrib)
    file.text = path
    return file


def generate_qrc(data: Tuple[str, str, str], root: str) -> str:
    # Main structure
    main_element = ElementTree.Element("RCC")

    prefix = ('/' if not data[0].startswith('/') else '') + data[0]
    str_path = data[1]
    root = Path(root)
    alias_prefix = data[2]

    root_path = solve_relative_path(Path(str_path))
    if not root_path.is_dir():
        return ''

    qresource = qrc_prefix(main_element, prefix)

    dirs = [root_path]

    while dirs:
        dir_path = dirs.pop()

        for path in dir_path.iterdir():
            if path.is_dir():
                dirs.append(path)
                continue

            abs_path = solve_relative_path(path)
            path = path.relative_to(root)

            qrc_file(qresource, str(path),
                     get_alias(abs_path, root_path, alias_prefix))

    string_tree: str = ElementTree.tostring(
        main_element, encoding='utf-8', xml_declaration=False).decode('utf-8')
    pretty_tree = minidom.parseString(string_tree).toprettyxml(indent=' ' * 4)

    pretty_tree = pretty_tree.split('\n', 1)[1]

    return pretty_tree


def make_qrc_files():
    for file, data in RESOURCES.items():

        if VERBOSITY > 0:
            print("Generating \"{}\" ...".format(file))

        file = solve_relative_path(file)

        contents = generate_qrc(data, str(file.parent))

        with open(file, 'w') as f:
            f.write(contents)


# ---- Generate from .qrc files ---------------------------------------------


def get_module_filename(res_file: str):
    path = PurePath(res_file)
    return path.stem + RESOURCE_SUFFIX + '.py'


def pyrcc5(root: str = None,
           threshold: str = None,
           compression: str = None,
           nocompression: bool = False):
    """
    Generate the qt resource module from .qrc files.

    The generated python modules contain the resources specified in the qt
    resource files. This commands calls `pyrcc5` with the parameters supplied.

    Parameters
    ----------
    root : str, optional
        The root directory to search the resources in, by default None
    threshold : str, optional
        The threshold for files to be compressed, by default None
    compression : str, optional
        The level of compression, by default None
    nocompression : bool, optional
        Whether to compress nothing, by default False
    """
    if not RESOURCE_FILES:
        if VERBOSITY > 0:
            print("No resource files specified.")

        return

    stdout = sys.stdout if VERBOSITY > 3 else subprocess.DEVNULL

    for qrc, pymod in RESOURCE_FILES.items():
        res_file = solve_relative_path(qrc)
        pyres_file = solve_relative_path(pymod)

        if res_file.is_dir() or not res_file.exists():
            continue

        if pyres_file.is_dir():
            pyres_file /= get_module_filename(res_file.name)

        # generate to file
        pyrcc5_cmd = ["pyrcc5", "-o", path(pyres_file)]

        if threshold:
            pyrcc5_cmd += ["-theshold", str(threshold)]

        if compression:
            pyrcc5_cmd += ["-compress", str(compression)]

        if nocompression:
            pyrcc5_cmd += ["-nocompress"]

        if root:
            pyrcc5_cmd += ["-root", str(root)]

        pyrcc5_cmd.append(path(res_file))

        if VERBOSITY > 3:
            print("Running \"", ' '.join(pyrcc5_cmd), '"', sep='')
        if VERBOSITY > 2:
            print("Generating python module for {} to {}.".format(
                res_file, pyres_file))
        elif VERBOSITY > 1:
            print("Generating python module for {}.".format(res_file))

        subprocess.run(pyrcc5_cmd, stdout=stdout, stderr=sys.stderr)


def pylupdate5(drop_obsolete: bool = False):
    """
    Update the translation files using `pylupdate5`.

    Parameters
    ----------
    drop_obsolete : bool, optional
        Whether to drop all obsolete strings, by default False
    """
    stdout = sys.stdout if VERBOSITY > 1 else subprocess.DEVNULL

    cmd = ["pylupdate5", "-translate-function", "_tr"]

    if drop_obsolete:
        cmd.append("-noobsolete")

    if VERBOSITY > 2:
        cmd.append("-verbose")

    cmd.append(str(solve_relative_path(PROJECT_FILE).as_posix()))

    if VERBOSITY > 3:
        print("Running \"", ' '.join(cmd), '"', sep='')
    elif VERBOSITY > 0:
        print("Running pylupdate5.")

    subprocess.run(cmd, stdout=stdout, stderr=sys.stderr)


if __name__ == "__main__":
    # ---- Define and configure the arg parser ------------------------------

    vinfo = "%(prog)s " + VERSION
    if argcomplete:
        vinfo += " completion"

    description = "A helper program automating common tasks" \
        " for PyQt5 projects."
    epilog = "The subcommands can be configured in the first section" \
        "of the `%(prog)s` script file. \n" + vinfo

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        allow_abbrev=True,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--version', action='version', version=vinfo)
    subparser = parser.add_subparsers(
        required=True,
        help="The subcommands running the different tasks",
        metavar="{task}")

    # the make_pro_file command
    parser_make_pro_file = subparser.add_parser(
        "projectfile",
        aliases=["pro", "make"],
        help="Automate the creation of the PyQt project file.")
    parser_make_pro_file.add_argument(
        "-d",
        "--dest",
        dest="filepath",  # default action is 'store'
        metavar="PATH",
        help="Override the path to the project file.")

    # the pyuic5 command
    parser_pyuic5 = subparser.add_parser(
        "pyuic5",
        aliases=["uic"],
        help="Automate running `pyuic5` for each .ui form file.")

    # the make_qrc command
    parser_qrc = subparser.add_parser(
        'makeres',
        aliases=['makeqrc', 'qrc'],
        help="Automate the creation of (some) qrc files.")

    # the pyrcc5 command
    parser_pyrcc5 = subparser.add_parser(
        "pyrcc5",
        aliases=["rcc"],
        help="Automate running `pyrcc5` for each .qrc resource file.")
    parser_pyrcc5.add_argument(
        "-c",
        "--compress",
        dest="compression",
        metavar="LEVEL",
        help="Set the compression level for all input files.")
    parser_pyrcc5.add_argument("--no-compress",
                               dest="nocompress",
                               action="store_true")
    parser_pyrcc5.add_argument(
        "-r",
        "--root",
        dest="root",
        metavar="PATH",
        help="Search all resource referenced in a .qrc file under PATH.")
    parser_pyrcc5.add_argument(
        "-t",
        "--threshold",
        dest="threshold",
        metavar="LEVEL",
        help="Set the threshold above which files should be compressed.")
    parser_pyrcc5.add_argument(
        '--nomake',
        '--no_make',
        '--nm',
        action='store_false',
        dest='make',
        help="Whether to regenerate the generated resource files.")

    # The pylupdate5 command
    parser_pylupdate5 = subparser.add_parser(
        "pylupdate5",
        aliases=["lupdate", "lu", "tfu"],
        help="Automate updating the translation files using `pylupdate5`.")
    parser_pylupdate5.add_argument(
        "--nogenerate",
        "--noregenerate",
        "--noremake",
        "--nomake",
        "--no",
        action="store_false",
        dest="remake",
        help=
        "Whether to regenerate the project file that is used by `pylupdate5`.")
    parser_pylupdate5.add_argument("--noobsolete", "--no-obsolete"
                                   "--drop",
                                   "--dropobsolete",
                                   "--drop-obsolete",
                                   action="store_true",
                                   dest="drop",
                                   help="Drop all obsolete strings.")

    # the all command
    parser_all = subparser.add_parser("all",
                                      help="Automate almost everything.")

    # verbosity
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-v",
        action="count",
        dest="verbosity",
        help="Specifing the option multiple times increases the verbosity.")
    verbosity_group.add_argument("--verbose",
                                 action="store",
                                 type=int,
                                 dest="verbosity",
                                 help="The verbosity of the program.")

    # ---- Handle ------------------------------------------------------------


    def command_projectfile(args: argparse.Namespace):
        global PROJECT_FILE
        PROJECT_FILE = args.filepath if args.filepath else PROJECT_FILE

        make_pro_file()

    def command_pyuic5(args: argparse.Namespace):
        pyuic5()

    def command_qrcfile(args: argparse.Namespace):
        make_qrc_files()

    def command_pyrcc5(args: argparse.Namespace):
        if args.make:
            make_qrc_files()

        pyrcc5(root=args.root,
               threshold=args.threshold,
               compression=args.compression,
               nocompression=args.nocompress)

    def command_pylupdate5(args: argparse.Namespace):
        if args.remake:
            make_pro_file()
        pylupdate5(drop_obsolete=args.drop)

    def all(args: argparse.Namespace):
        make_pro_file()
        pyuic5()
        make_qrc_files()
        pyrcc5()
        pylupdate5()

    parser_make_pro_file.set_defaults(func=command_projectfile)
    parser_pyuic5.set_defaults(func=command_pyuic5)
    parser_qrc.set_defaults(func=command_qrcfile)
    parser_pyrcc5.set_defaults(func=command_pyrcc5)
    parser_pylupdate5.set_defaults(func=command_pylupdate5)
    parser_all.set_defaults(func=all)

    # ---- Completion --------------------------------------------------------

    if argcomplete:
        argcomplete.autocomplete(parser)

    # Handle args
    args = parser.parse_args()

    VERBOSITY = args.verbosity if args.verbosity else VERBOSITY

    args.func(args)
