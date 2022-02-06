
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import QtGui
from qgis.PyQt import uic
import os.path

from qgis._core import QgsFeature

from .addannotationdialog import AddAnnotationDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/annotationdialog.ui'))
class AnnotateDialog(QDialog,FORM_CLASS):
	
    def __init__(self,selectedresources,activelayer,selectiongeometry,resultlayer=None):
        super(AnnotateDialog, self).__init__()
        self.setupUi(self)
        model = QtGui.QStandardItemModel()
        self.selectiongeometry=selectiongeometry
        self.selectionListView.setModel(model)
        self.addAnnotationButton.clicked.connect(lambda: AddAnnotationDialog(self.selectionListView).exec())
        self.editAnnotationButton.clicked.connect(self.editAnnotationFunc)
        self.removeAnnotationButton.clicked.connect(lambda: self.selectionListView.removeItem(self.selectionListView.currentIndex()))
        self.applyButton.clicked.connect(self.applyAnnotationToLayer)
        for i in selectedresources:
            item = QtGui.QStandardItem(str(activelayer.name())+": "+str(i.id()))
            model.appendRow(item)
        self.show()

    def editAnnotationFunc(self):
        selected=self.selectionListView.selectionModel().selectedIndexes()[0]
        AddAnnotationDialog(self.selectionListView,selected.data(256),selected.data(257))

    """Creating a specifically modified vector layer which could be converted to JSON-LD (W3C Web Annotation Data Model)"""
    def applyAnnotationToLayer(self):
        feature=QgsFeature()
        feature.setGeometry(self.selectiongeometry)
        for index in self.selectionListView.rowCount():
            print("For each item create column and row values")


