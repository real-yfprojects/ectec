#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automate building using doit.

***********************************

Created on 2022/05/26 at 08:59:16

Copyright (C) 2022 real-yfprojects (github.com user)

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
import os
import re
import shutil
import sys
from importlib.machinery import SOURCE_SUFFIXES
from pathlib import Path, PurePath
from typing import Dict, List, Tuple
from xml.dom import minidom
from xml.etree import ElementTree

import defusedxml.ElementTree as defusedET
import virtualenv
from doit import task_params
from doit.action import CmdAction
from doit.tools import config_changed

# ---- Configuration ---------------------------------------------------------

#: Path to project file relative to this script.
PROJECT_FILE = "project.pro"

#: List of paths to source files or directories relative to this script.
SOURCES = ["src/ectecgui/"]

#: List of temporary directories not to include in sources.
SOURCES_TEMP_DIRS = ["__pycache__"]

#: List of endings for source files.
SOURCE_REGEX = re.compile(r'.*/(?!ui_)[^/]+(?<!_res)(' +
                          '|'.join(SOURCE_SUFFIXES) + r')')

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
    "res/clientUser.ui": 'src/ectecgui/client/userclient/ui_main.py',
    "res/about.ui": 'src/ectecgui/about/ui_about.py'
}

#: List of paths for translation files relative to this script.
TRANSLATIONS = ["res/ectecgui.de.ts"]

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
                    pattern: re.Pattern = None,
                    exclude_dir_names: List[str] = []) -> List[Path]:
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
            if element.is_dir() and element.name not in exclude_dir_names:
                directories_left.append(element.resolve())
            elif not pattern or pattern.fullmatch(
                    element.resolve().as_posix()):
                files.append(element.resolve())

    return files


source_files = None


def get_source_files():
    global source_files
    if source_files is None:
        source_files = files_recursive(SOURCES, SOURCE_REGEX,
                                       SOURCES_TEMP_DIRS)
    return source_files


def make_pro_file():
    """
    Generate and write the .pro project file of the PyQt project.

    The .pro project file is needed for the `pylupdate5` command.
    """
    content = ""

    # Make List of Sources
    source_files = get_source_files()

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

    content += generate_file_list("SOURCES", source_files, length)
    content += generate_file_list("RESOURCES", resource_files, length)
    content += generate_file_list("FORMS", form_files, length)
    content += generate_file_list("TRANSLATIONS", trans_files, length)

    # write file
    filepath = solve_relative_path(PROJECT_FILE)

    with filepath.open('w') as file:
        file.write(content)


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


def generate_qrc(data: Tuple[str, str, str], root: Path) -> str:
    # Main structure
    main_element = ElementTree.Element("RCC")

    prefix = ('/' if not data[0].startswith('/') else '') + data[0]
    str_path = data[1]
    alias_prefix = data[2]

    root_path = solve_relative_path(str_path)
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

            abs_path = path.absolute()
            path = path.relative_to(root)

            qrc_file(qresource, str(path),
                     get_alias(abs_path, root_path, alias_prefix))

    string_tree: str = ElementTree.tostring(
        main_element, encoding='utf-8', xml_declaration=False).decode('utf-8')
    pretty_tree = minidom.parseString(string_tree).toprettyxml(indent=' ' * 4)

    pretty_tree = pretty_tree.split('\n', 1)[1]

    return pretty_tree


# ---- Generate resource files -----------------------------------------------


def get_module_filename(res_file: str):
    path = PurePath(res_file)
    return path.stem + RESOURCE_SUFFIX + '.py'


# ---- Build Rules -----------------------------------------------------------

DOIT_CONFIG = {
    'action_string_formatting': 'new',
    'default_tasks': [
        'rcc',
        'uic',
    ]
}


def string_title(title: str):
    """Set a string title for a task."""

    def get_title(task):
        return title

    return get_title


res_file_cache: Dict[str, list] = {}


def files_for_resource(resource: str):
    """
    Get a list of files that included in a resource file.

    The results are cached.
    """
    file_list = res_file_cache.get(resource)
    if file_list is None:
        if resource in RESOURCES:
            data = RESOURCES[resource]
            file_list = [
                p for p in solve_relative_path(data[1]).glob('**/*')
                if p.is_file()
            ]
            res_file_cache[resource] = file_list
        else:
            # extract from file
            file_path = solve_relative_path(resource)
            tree = defusedET.parse(file_path.open())
            file_list = [
                Path(file_path.parent, file_tag.text).resolve()
                for file_tag in tree.findall('.//file')
            ]

    return file_list


def task_qrc():
    """Automate the writing of qrc files."""

    def write(file: Path, data):
        contents = generate_qrc(data, file.parent)
        with open(file, 'w') as f:
            f.write(contents)

    for file, data in RESOURCES.items():
        path = solve_relative_path(file)
        files = files_for_resource(file)
        yield {
            'name': file,
            'uptodate': [config_changed({'files': [str(f) for f in files]})],
            'targets': [path],
            'actions': [(write, [path, data])],
        }


def task_uic():
    """
    Generate the form python modules from the .ui form files.
    """
    for form, pymod in FORMS.items():
        form_file = solve_relative_path(form)
        pyui_file = solve_relative_path(pymod)
        if not form_file.is_dir() and not pyui_file.is_dir():
            # generate to file
            yield {
                'name':
                form,
                'targets': [pyui_file],
                'file_dep': [form_file],
                'actions': [[
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
                ]]
            }


def task_rcc():
    """Compile the resource files."""
    for qrc, pymod in RESOURCE_FILES.items():
        res_file = solve_relative_path(qrc)
        pyres_file = solve_relative_path(pymod)

        if res_file.is_dir() or not res_file.exists():
            continue

        if pyres_file.is_dir():
            pyres_file /= get_module_filename(res_file.name)

        # if threshold:
        #     pyrcc5_cmd += ["-theshold", str(threshold)]

        # if compression:
        #     pyrcc5_cmd += ["-compress", str(compression)]

        # if nocompression:
        #     pyrcc5_cmd += ["-nocompress"]

        # if root:
        #     pyrcc5_cmd += ["-root", str(root)]

        files = files_for_resource(qrc)
        yield {
            'name': qrc,
            'targets': [pyres_file],
            'file_dep': [res_file] + files,
            'actions': [["pyrcc5", "-o",
                         path(pyres_file),
                         path(res_file)]]
        }


def task_pro():
    """
    Generate and write the .pro project file of the PyQt project.

    The .pro project file is needed for the `pylupdate5` command.
    """
    sources = [str(f) for f in get_source_files()]

    return {
        'uptodate': [
            config_changed({
                'resources': list(RESOURCES),
                'forms': list(FORMS),
                'translations': TRANSLATIONS,
                'sources': sources,
            })
        ],
        'targets': [solve_relative_path(PROJECT_FILE)],
        'actions': [make_pro_file],
        'clean':
        True,
        'verbosity':
        2,
    }


@task_params([{
    'name': 'drop_obsolete',
    'short': '',
    'long': 'drop-obsolete',
    'type': bool,
    'default': False,
    'help': 'Drop all obsolete strings in the translation files.'
}])
def task_lupdate(drop_obsolete):
    """
    Update the translation files using `pylupdate5`.

    Parameters
    ----------
    drop_obsolete : bool, optional
        Whether to drop all obsolete strings, by default False
    """
    cmd = [
        "pylupdate5",
        "-verbose",
        "-translate-function",
        "_tr",
    ]
    if drop_obsolete:
        cmd.append('-noobsolete')
    cmd.append(str(solve_relative_path(PROJECT_FILE).as_posix()))

    sources = get_source_files()
    form_files = [solve_relative_path(form) for form in FORMS]

    return {
        'targets': [solve_relative_path(file) for file in TRANSLATIONS],
        'file_dep': [solve_relative_path(PROJECT_FILE)] + sources + form_files,
        'actions': [cmd],
        'verbosity': 2,
        'uptodate': [config_changed({'drop_obsolete': drop_obsolete})],
    }


@task_params([{
    'name':
    'remove_identical',
    'long':
    'noident',
    'type':
    bool,
    'default':
    False,
    'help':
    'If the translated text is the same as the source text, '
    'do not include the message'
}, {
    'name': 'no_unfinished',
    'long': 'no-unfinished',
    'type': bool,
    'default': False,
    'help': 'Do not include unfinished translations'
}, {
    'name':
    'mark_untranslated',
    'short':
    'm',
    'long':
    'mark',
    'type':
    str,
    'default':
    '',
    'help':
    'If a message has no real translation, use the source text '
    'prefixed with the given string instead'
}])
def task_lrelease(remove_identical, no_unfinished, mark_untranslated):
    """Compile `.ts` translation files into `.qm` binary translations files."""

    cmd = ["lrelease"]
    if remove_identical:
        cmd.append('-removeidentical')
    if no_unfinished:
        cmd.append('-nounfinished')
    if mark_untranslated:
        cmd.extend(['-markuntranslated', mark_untranslated])
    cmd.append(str(solve_relative_path(PROJECT_FILE).as_posix()))

    ts_files = [solve_relative_path(f) for f in TRANSLATIONS]
    qm_files = [tsf.parent / (tsf.stem + '.qm') for tsf in ts_files]
    return {
        'targets':
        qm_files,
        'file_dep':
        ts_files,
        'actions': [cmd],
        'verbosity':
        2,
        'uptodate': [
            config_changed({
                'remove_identical': remove_identical,
                'no_unfinished': no_unfinished,
                'mark_untranslated': mark_untranslated
            })
        ],
        'clean':
        True,
    }


# ---- Run Rules -------------------------------------------------------------


@task_params([{
    'name': 'build',
    'long': 'build',
    'type': bool,
    'default': True,
    'inverse': 'skip-build',
    'help': 'Skip building the source files.'
}])
def task_client(build):
    """Start the client."""
    return {
        'task_dep': ['rcc', 'uic'] if build else [],
        'actions': [CmdAction('python3 -m ectecgui.client', cwd='./src/')],
        'verbosity': 2,
        'uptodate': [False],
    }


@task_params([{
    'name': 'build',
    'long': 'build',
    'type': bool,
    'default': True,
    'inverse': 'skip-build',
    'help': 'Skip building the source files.'
}])
def task_server(build):
    """Start the server."""
    return {
        'task_dep': ['rcc', 'uic'] if build else [],
        'actions': [CmdAction('python3 -m ectecgui.server', cwd='./src/')],
        'verbosity': 2,
        'uptodate': [False],
    }


# ---- Virtual Environments --------------------------------------------------


def create_venv(path: Path) -> virtualenv.run.Session:
    """Create a virtual python environment at the given path."""
    virtualenv.cli_run([str(path.resolve())])


def source_venv(path: Path):
    """Prepare a bash environment."""
    environment = os.environ.copy()
    environment['VIRTUAL_ENV'] = str(path.resolve())
    if sys.platform == 'win32':
        script_path = 'Scripts'
    else:
        script_path = 'bin'
    environment['PATH'] = str(
        (path / script_path).resolve()) + os.pathsep + environment['PATH']
    environment.pop('PYTHON_HOME', None)

    return environment


def CmdInVenv(venv: Path, cmd, **kwargs):
    """Run task action in a virtual env"""
    kwargs.setdefault('env', {}).update(source_venv(venv))
    if isinstance(cmd, list):
        kwargs.setdefault('shell', False)
    # kwargs.setdefault('executable', '/usr/bin/bash')
    return CmdAction(cmd, **kwargs)


# ---- Package Rules ---------------------------------------------------------

TEMP_ENV_PATH = 'tempenv'


def temp_env_available():
    path = solve_relative_path(TEMP_ENV_PATH)

    return path.exists()


def task_temp_env():
    """Create a virtual environment for packaging."""
    venv = solve_relative_path(TEMP_ENV_PATH)
    return {
        'actions': [
            (shutil.rmtree, [venv, True]),
            (create_venv, [venv]),
            CmdInVenv(venv, 'pip install -U build'),
        ],
        'uptodate': [False],
        'title':
        string_title(
            f'Setting up virtual python environment at {TEMP_ENV_PATH}...'),
    }


def task_build():
    """Build ectecgui python package."""
    venv = solve_relative_path(TEMP_ENV_PATH)
    return {
        'task_dep': ['temp_env'],
        'actions': [CmdInVenv(venv, 'python -m build')],
        'verbosity': 2,
    }


def task_setup_packaging():
    """Install ectec and ectecgui package in tempenv."""
    venv = solve_relative_path(TEMP_ENV_PATH)
    return {
        'task_dep': ['temp_env'],
        'actions': [
            CmdInVenv(venv, 'pip install .'),
            CmdInVenv(venv, 'pip install -U PyInstaller')
        ],
        'title':
        string_title('Install the ectec packages and pyinstaller in venv...'),
    }


def task_bundle_pyinstaller():
    venv = solve_relative_path(TEMP_ENV_PATH)
    return {
        'task_dep': ['setup_packaging'],
        'actions':
        [CmdInVenv(venv, 'python -m PyInstaller --noconfirm pyinstall.spec')],
        'verbosity':
        2,
    }
