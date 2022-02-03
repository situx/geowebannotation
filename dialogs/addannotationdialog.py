from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt import uic
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/addannotationdialog.ui'))


class AddAnnotationDialog(QDialog, FORM_CLASS):

    def __init__(self, selectedresources, activelayer):
        super(AddAnnotationDialog, self).__init__()
        self.setupUi(self)
        self.show()