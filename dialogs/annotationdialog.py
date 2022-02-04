
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt import QtGui
from qgis.PyQt import uic
import os.path

from .addannotationdialog import AddAnnotationDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/annotationdialog.ui'))
class AnnotateDialog(QDialog,FORM_CLASS):
	
    def __init__(self,selectedresources,activelayer):
        super(AnnotateDialog, self).__init__()
        self.setupUi(self)
        model = QtGui.QStandardItemModel()
        self.selectionListView.setModel(model)
        self.addAnnotationButton.clicked.connect(lambda: AddAnnotationDialog(self.selectionListView).exec())
        self.editAnnotationButton.clicked.connect(self.editAnnotationFunc)
        self.removeAnnotationButton.clicked.connect(lambda: self.selectionListView.removeItem(self.selectionListView.currentIndex()))
        for i in selectedresources:
            item = QtGui.QStandardItem(str(activelayer.name())+": "+str(i.id()))
            model.appendRow(item)
        self.show()

    def editAnnotationFunc(self):
        selected=self.selectionListView.selectionModel().selectedIndexes()[0]
        AddAnnotationDialog(self.selectionListView,selected.data(256),selected.data(257))

