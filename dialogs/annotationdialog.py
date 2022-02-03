
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt import QtGui
from qgis.PyQt import uic
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/annotationdialog.ui'))
class AnnotateDialog(QDialog,FORM_CLASS):
	
    def __init__(self,selectedresources,activelayer):
        super(AnnotateDialog, self).__init__()
        self.setupUi(self)
        model = QtGui.QStandardItemModel()
        self.selectionListView.setModel(model)
        for i in selectedresources:
            item = QtGui.QStandardItem(str(activelayer.name())+": "+str(i.id()))
            model.appendRow(item)
        self.show()
         
