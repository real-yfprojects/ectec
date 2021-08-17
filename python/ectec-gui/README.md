# Ectec GUI

This is the python package containing the official graphical application (GUI) of the Ectec chattool.
The GUI uses the ectec package as a back-end.

- [Ectec GUI](#ectec-gui)
  - [Development](#development)
    - [Testing](#testing)
    - [QT Resource System](#qt-resource-system)
    - [QT Designer and `.ui` files](#qt-designer-and-ui-files)
    - [QT Internationalization](#qt-internationalization)

## Development

### Testing

Before running the code you should make sure all resources are compiled.
Usually a simply running the following command should be sufficient.

```bash
$ ./automate.py all
```
### QT Resource System

The qt resource system allows resources which are files used by the application to be embedded inside a python module.
This python module can then be imported to make the contained resources accessible to the application and its code.
The advantage of this approach is that it is way easier to package the resources along the python code.

To use the resources specified inside a qt resource file named `assets.qrc` in this example, follow these steps:

1. Configure the resource file in `automate.py`:

   ```python
   RESOURCES = {...,
      "path/to/assets.qrc" : "parent/directory/of/python/module/"
   }

2. Run the following command inside this file's directory with `PyQt5` installed.

   ```bash
   $ ./automate.py rcc
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

1. Configure the form file in `automate.py`.

   ```python
   FORMS = {...,
            "path/to/form.ui" : "path/to/python/module.py"}
   ```

2. Run the following command inside this file's directory with `PyQt5` installed.

   ```bash
   $ ./automate.py uic
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
translation file. This file can be opened with *QT Linguist* to translate the strings into a target language and store
the translation in the translation file as well.

It is importent to wrap every UI string with a call to the `QtApplication`'s translate function so that it is
translated on runtime and can also be found by `pylupdate5`. To save effort the following line is added to each module
implementing parts of the UI, right below the import statements:

```python
_tr = QtApplication.translate
```

The strings that should be translated should then be wrapped by `_tr`:
```python
dialog.setTitle(_tr("The title in developer English"))
```

To get the `.ts` translation files from the code and the forms the forms have to be configured in `automate.py` as
described [above](#qt-designer-and-ui-files). The translation files wished have to be configured like that:

```python
TRANSLATIONS = ["res/ectecgui.en.ts", "res/ectecgui.de.ts"]
```

The dot between `ectecgui` and the *language code* must be in place.
The `.ts` files can be created or updated by running the following in this
files directory:

```bash
$ ./automate.py lupdate
```

The `.ts` translation files should be converted into a `.qm` optimized translation file for use in the application.
