# Ectec GUI

This is the python package containing the official graphical application (GUI)
of the Ectec chattool.
The GUI uses the ectec package which is contained in the packaged python
distribution as a back-end.

-   [Ectec GUI](#ectec-gui)
    -   [Building from Source](#building-from-source)
        -   [Building the python package](#building-the-python-package)
        -   [Building the PyInstaller distributable](#building-the-pyinstaller-distributable)
    -   [Development](#development)
        -   [Testing](#testing)
        -   [QT Resource System](#qt-resource-system)
        -   [QT Designer and `.ui` files](#qt-designer-and-ui-files)
        -   [QT Internationalization](#qt-internationalization)

## Building from Source

You will need a complete _Python 3_ installation for the following steps.
And you will need to know how to call the commands `python` or `pip` from
the command line. Often these commands have a slightly different name:
`python3` and `pip3`.

### Building the python package

1. Install the `build` and the `wheel` python package.

    ```bash
    > pip install -U build wheel
    ```

2. Enter the directory of this file (python/ectecgui/).

3. Build the python package.

    ```bash
    > python -m build -s -w
    ```

The wheel and the source distributable python package can now be found in
the dist folder.

### Building the PyInstaller distributable

1. Create a virtual python environment in the folder `env`:

    ```bash
    > python -m venv env
    ```

2. Enter/source the virtual environment. In bash type:

    ```bash
    > source env/bin/activate
    ```

3. Enter the directory `python/ectecgui` of this repository.

4. Install `ectec` and `ectecgui` in the virtual environment.

    ```bash
    > python install .
    ```

5. Run pyinstaller.

    ```bash
    > python -m PyInstaller pyinstall.spec
    ```

6. You will find the distributable build (the `Ectec` folder) in `./dist/`.

## Development

### Testing

Before running the code you should make sure all resources are compiled.
For that you will need to install the python package `doit`.
Then enter the directory of this file with your favourite terminal and run:

```bash
> doit
.  qrc:res/breeze.qrc
.  rcc:res/breeze.qrc
.  uic:res/clientConnect.ui
.  uic:res/clientUser.ui
.  uic:res/server.ui
.  uic:res/about.ui
.  pro
.  lupdate
.  lrelease
.  rcc:res/ectec.qrc
```

### QT Resource System

The qt resource system allows resources which are files used by the application to be embedded inside a python module.
This python module can then be imported to make the contained resources accessible to the application and its code.
The advantage of this approach is that it is way easier to package the resources along the python code.

To use the resources specified inside a qt resource file named `assets.qrc` in this example, follow these steps:

1. Configure the resource file in `dodo.py`:

    ```python
    RESOURCES = {...,
       "path/to/assets.qrc" : "parent/directory/of/python/module/"
    }

    ```

2. Run the build command that was introduced previously with `PyQt5` installed.

    ```bash
    > doit
    -- qrc:res/breeze.qrc
    -- rcc:res/breeze.qrc
    .  rcc:path/to/assets.qrc
    -- uic:res/clientConnect.ui
    -- uic:res/clientUser.ui
    -- uic:res/server.ui
    -- uic:res/about.ui
    -- pro
    -- lupdate
    -- lrelease
    -- rcc:res/ectec.qrc
    ```

3. A python module named `assets_res.py` was created in the directory specified.
   Import the python module in the python code you want to use the resources in.

    ```python
    import assets_res
    ```

4. You can access the resources when using the qt framework by starting the path with `:`.
   If you defined an image file with the path `images/icon.png` in the resource file you will be able to access it
   e.g. using `QtCore.QFile` like so:

    ```python
    file = QtCore.QFile(':/images/icon.png')
    ```

### QT Designer and `.ui` files

Use the QT resource system for pictures and other resources. You can also add existing resource file
inside _QT Designer_ to use its resources in the GUI.

To use a UI from an `.ui`-File follow these steps:

1. Configure the form file in `dodo.py`.

    ```python
    FORMS = {...,
             "path/to/form.ui" : "path/to/python/module.py"}
    ```

2. Run the build command that was introduced previously with `PyQt5` installed.

    ```bash
    > doit
    -- qrc:res/breeze.qrc
    -- rcc:res/breeze.qrc
    -- uic:res/clientConnect.ui
    -- uic:res/clientUser.ui
    -- uic:res/server.ui
    -- uic:res/about.ui
    .  uic:path/to/form.ui
    -- pro
    -- lupdate
    -- lrelease
    -- rcc:res/ectec.qrc
    ```

3. Create import statements of as the following in the `__init__` of the module with the python _ui_ object class.
   This allows the UI to import the resource file's python module from within the same module.

    Example:

    ```python
    import ..ectec_res as ectec_res
    ```

4. Import the UI in the module you want to implement the `QDialog`.

    Example:

    ```python
    from .maindialog import Ui_Main
    ```

5. Load the UI inside the dialog's init method.

    Example:

    ```python
    self.ui = Ui_Main()
    self.ui.setupUi(self)
    ```

### QT Internationalization

The QT framework provides a bunch of tools for internationalization that allow the GUI to be available
in multiple languages. The `lupdate` or `pylupdate5` command collects the strings to be translated into a `.ts`
translation file. This file can be opened with _QT Linguist_ to translate the strings into a target language and store
the translation in the translation file as well.

It is importent to wrap every UI string with a call to the `QtApplication`'s translate function so that it is
translated on runtime and can also be found by `pylupdate5`. To save effort the following line is added to each module
implementing parts of the UI, right below the import statements:

```python
_tr = QtApplication.translate
```

The strings that should be translated should then be wrapped by `_tr`:

```python
dialog.setTitle(_tr("The context of the string",
                    "The title in developer English"))
```

In very rare cases you will want to mark a string for translation without
translating it yet. For that you can use the method `translate` that is
defined in `ectecgui.helpers`. It will simply return the arguments passed
to it as a tuple. You use it in the same way as `_tr` before but store the
return value in a variable. Later you can than pass the arguments stored
in that variable to `_tr` so that they are actually translated:

```python
from .helpers import translate

some_text = translate("Context", "Some text")

# the `*` is important so that the tuple will be unpacked.
label.setText(_tr(*some_text))
```

To get the `.ts` translation files from the code and the forms the forms have to be configured in `dodo.py` as
described [above](#qt-designer-and-ui-files). The translation files wished have to be configured like that:

```python
TRANSLATIONS = ["res/ectecgui.en.ts", "res/ectecgui.de.ts"]
```

The dot between `ectecgui` and the _language code_ must be in place.
The `.ts` files can be created or updated by running the previously introduced
build command:

```bash
> doit
-- qrc:res/breeze.qrc
-- rcc:res/breeze.qrc
-- uic:res/clientConnect.ui
-- uic:res/clientUser.ui
-- uic:res/server.ui
-- uic:res/about.ui
-- pro
.  lupdate
.  lrelease
.  rcc:res/ectec.qrc
```

The `.ts` translation files should be converted into a `.qm` optimized translation file for use in the application.
