from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QLineEdit
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt import uic
import os.path

from ..util.uiutils import UIUtils
from .searchdialog import SearchDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/addannotationdialog.ui'))

class AddAnnotationDialog(QDialog, FORM_CLASS):

    def __init__(self, selectionListView,target,triplestoreconf,annotationrel="",annotationcontent=""):
        super(AddAnnotationDialog, self).__init__()
        self.setupUi(self)
        self.selectionListView=selectionListView
        self.triplestoreconf=triplestoreconf
        self.target=target
        self.annotationTypeCBox.currentIndexChanged.connect(self.annotationTypeChanged)
        self.cancelButton.clicked.connect(self.close)
        self.searchRelationButton.setIcon(UIUtils.searchclassicon)
        self.searchRelationButton2.setIcon(UIUtils.searchclassicon)
        self.searchRelationButton.clicked.connect(lambda: self.buildSearchDialog(-1,-1,False,None,1,False,None,None))
        self.searchRelationButton2.clicked.connect(lambda: self.buildSearchDialog(-1, -1, False, None, -1, False, None, None))
        self.addAnnotationButton.clicked.connect(self.saveAnnotation)
        self.stackedWidget.setCurrentIndex(1)
        self.show()

    def buildSearchDialog(self,row=-1, column=-1, interlinkOrEnrich=False, table=None, propOrClass=1, bothOptions=False,
                          currentprefixes=None, addVocabConf=None):
        self.currentcol = column
        self.currentrow = row
        self.interlinkdialog = SearchDialog(column, row, self.triplestoreconf, None, interlinkOrEnrich, table,
                                            propOrClass, bothOptions, currentprefixes, addVocabConf)
        self.interlinkdialog.setMinimumSize(650, 400)
        self.interlinkdialog.setWindowTitle("Search Interlink Concept")
        self.interlinkdialog.exec_()


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

