
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt import QtGui
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt import uic
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'annotationdialog.ui'))
class AnnotateDialog(QDialog,FORM_CLASS):
	
    def __init__(self,selectedresources):
        super(QDialog, self).__init__()
        self.setupUi(self)
        msgBox=QMessageBox()
        msgBox.setText("hello");
        msgBox.exec();
        model = QtGui.QStandardItemModel()
        self.selectionListView.setModel(model)
        msgBox=QMessageBox()
        msgBox.setText(str(selectedresources));
        msgBox.exec();
        for i in selectedresources:
            print(i)
            msgBox=QMessageBox()
            msgBox.setText(str(i));
            msgBox.exec();
            item = QtGui.QStandardItem(i)
            model.appendRow(item)
            
         