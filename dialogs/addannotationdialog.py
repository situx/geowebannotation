from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QLineEdit
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt import uic
import os.path

from ..util.uiutils import UIUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/addannotationdialog.ui'))

class AddAnnotationDialog(QDialog, FORM_CLASS):

    def __init__(self, selectionListView,target,annotationrel="",annotationcontent=""):
        super(AddAnnotationDialog, self).__init__()
        self.setupUi(self)
        self.selectionListView=selectionListView
        self.target=target
        self.annotationTypeCBox.currentIndexChanged.connect(self.annotationTypeChanged)
        self.cancelButton.clicked.connect(self.close)
        self.addAnnotationButton.clicked.connect(self.saveAnnotation)
        self.show()

    def annotationTypeChanged(self):
        if self.annotationTypeCBox.currentText()=="TextAnnotation":
            self.stackedWidget.setCurrentIndex(1)
        elif self.annotationTypeCBox.currentText()=="Semantic Web":
            self.stackedWidget.setCurrentIndex(0)

    def saveAnnotation(self):
        if self.annotationTypeCBox.currentText()=="TextAnnotation" and self.textAnnotationEdit.toPlainText()!="":
            self.textAnnotationEdit.show()
            item=QStandardItem()
            item.setText("TextAnnotation: "+self.textAnnotationEdit.toPlainText()[0:100])
            item.setData("TextAnnotation",UIUtils.dataslot_annotype)
            item.setData(self.textAnnotationEdit.toPlainText(),UIUtils.dataslot_annocontent)
            item.setData(self.licenseComboBox.currentText(), UIUtils.dataslot_annolicense)
            item.setData(self.annotationMotivationComboBox.currentText(), UIUtils.dataslot_annomotivation)
            item.setData(self.target, UIUtils.dataslot_target)
            item.setData(self.textAnnotationEdit.toPlainText(),UIUtils.dataslot_annovalue)
            item.setData("http://www.w3.org/2001/XMLSchema#string", UIUtils.dataslot_annotype)
            item.setData(self.creatorLineEdit.text(), UIUtils.dataslot_annocreator)
            item.setData(self.chooseLanguageComboBox.currentText(), UIUtils.dataslot_language)
            self.selectionListView.appendRow(item)
            self.close()
        elif self.annotationTypeCBox.currentText()=="TextAnnotation" and self.textAnnotationEdit.toPlainText()!="":
            item=QStandardItem()
            item.setText("TextAnnotation: "+self.textAnnotationEdit.toPlainText()[0:100])
            item.setData("TextAnnotation",UIUtils.dataslot_annotype)
            item.setData(self.textAnnotationEdit.toPlainText(),UIUtils.dataslot_annocontent)
            item.setData(self.licenseComboBox.currentText(), UIUtils.dataslot_annolicense)
            item.setData(self.annotationMotivationComboBox.currentText(), UIUtils.dataslot_annomotivation)
            item.setData(self.target, UIUtils.dataslot_target)
            item.setData(self.textAnnotationEdit.toPlainText(),UIUtils.dataslot_annovalue)
            item.setData("http://www.w3.org/2001/XMLSchema#string", UIUtils.dataslot_annotype)
            item.setData(self.creatorLineEdit.text(), UIUtils.dataslot_annocreator)
            item.setData(self.chooseLanguageComboBox.currentText(), UIUtils.dataslot_language)
            self.selectionListView.appendRow(item)
            self.close()

