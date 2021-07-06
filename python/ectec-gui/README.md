# Ectec GUI

This is the python package containing the official graphical application (GUI) of the Ectec chattool. The GUI uses the ectec package as a back-end.

## Development

### QT Designer and `.ui` files

Use the QT resource system for pictures and other resources. You can also add existing resource file inside *QT Designer* to use its resources in the GUI.

To use a UI from an `.ui`-File follow these steps:

1. Run the following command inside a terminal with `PyQt5` installed.

   ```bash
   pyuic5 <ui-file> -o <python-module-file-for-ui> --import-from '.' --resource-suffix '_res'
   ```

2. Create import statements of as the following in the `__init__` of the module with the python *ui* object class. This allows the UI to import the resource file's python module from within the same module.

   Example:
   ```python
   import ..ectec_res as ectec_res
   ```

3. Import the UI in the module you want to implement the `QDialog`.

   Example:
   ```python
   from .maindialog import Ui_Main
   ```

4. Load the UI inside the dialog's init method.

   Example:
   ```python
   self.ui = Ui_Main()
   self.ui.setupUi(self)
   ```
