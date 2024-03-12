import uuid

from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt import QtGui
from qgis.PyQt import uic
import os.path
from qgis.core import Qgis, QgsMessageLog
from qgis.core import QgsFeature, QgsVectorLayer, QgsField, QgsProject

from ..util.ui.uiutils import UIUtils
from .addannotationdialog import AddAnnotationDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/annotationdialog.ui'))

MESSAGE_CATEGORY="GeoWebAnnotation"

class AnnotationDialog(QDialog, FORM_CLASS):
	
    def __init__(self,selectedresources,activelayer,selectiongeometry,triplestoreconf,languagemap={},resultlayer=None):
        super(AnnotationDialog, self).__init__()
        self.setupUi(self)
        self.selectedresources = selectedresources
        self.triplestoreconf=triplestoreconf
        self.model = QtGui.QStandardItemModel()
        self.model2 = QtGui.QStandardItemModel()
        self.selectiongeometry=selectiongeometry
        self.activelayer=activelayer
        self.selectionListView.setModel(self.model)
        self.annotationListView.setModel(self.model2)
        self.addAnnotationButton.clicked.connect(lambda: AddAnnotationDialog(self.model2,self.activelayer.name(),self.triplestoreconf).exec())
        self.editAnnotationButton.clicked.connect(self.editAnnotationFunc)
        self.removeAnnotationButton.clicked.connect(lambda: self.selectionListView.removeItem(self.selectionListView.currentIndex()))
        self.applySelectionGeoButton.clicked.connect(self.applyAnnotationToLayer)
        self.applySelectedGeomsButton.clicked.connect(self.applyAnnotationContentsToLayer)
        QgsMessageLog.logMessage('Started task "{}"'.format(selectedresources), MESSAGE_CATEGORY, Qgis.Info)
        for i in selectedresources:
            item = QStandardItem(str(activelayer.name())+": "+str(i.id()))
            self.model.appendRow(item)
        if resultlayer==None:
            self.resultlayer=QgsVectorLayer("Polygon", str(activelayer.name())+"_AnnotationLayer", "memory")
            self.pr = self.resultlayer.dataProvider()
            self.pr.addAttributes([
                              QgsField("id", QVariant.String),
                              QgsField("motivation", QVariant.String),
                              QgsField("type", QVariant.String),
                              QgsField("license", QVariant.String),
                              QgsField("creator", QVariant.String),
                              QgsField("relation", QVariant.String),
                              QgsField("target", QVariant.String),
                              QgsField("body.language", QVariant.String),
                              QgsField("body.value", QVariant.String),
                              QgsField("body.valuetype", QVariant.String)
                            ])
            self.resultlayer.updateFields()
        else:
            self.resultlayer=resultlayer
        self.show()

    def editAnnotationFunc(self):
        selected=self.selectionListView.selectionModel().selectedIndexes()[0]
        AddAnnotationDialog(self.model2,self.activelayer.name(),self.triplestoreconf,selected.data(UIUtils.dataslot_conceptURI),selected.data(UIUtils.dataslot_annocontent))


    def applyAnnotationContentsToLayer(self):
        self.resultlayer.startEditing()
        feats=[]
        annoperfeat={}
        for instance in self.selectedresources:
            QgsMessageLog.logMessage('Started task "{}"'.format(instance), MESSAGE_CATEGORY, Qgis.Info)
            if str(instance.id()) not in annoperfeat:
                annoperfeat[str(instance.id())]=0
            annoperfeat[str(instance.id())]+=1
            findex=0
            for index in range(self.model2.rowCount()):
                feature = QgsFeature()
                # feature.setGeometry(instance.geometry())
                feature.setId(findex)
                addarray=[
                    str(self.model2.item(index).data(UIUtils.dataslot_target))+"_"+str(instance.id())+"_anno",
                    str(self.model2.item(index).data(UIUtils.dataslot_annomotivation)),
                    str(self.model2.item(index).data(UIUtils.dataslot_annotype)),
                    str(self.model2.item(index).data(UIUtils.dataslot_annolicense)),
                    str(self.model2.item(index).data(UIUtils.dataslot_annocreator)),
                    str(self.model2.item(index).data(UIUtils.dataslot_relation)),
                    str(self.model2.item(index).data(UIUtils.dataslot_target))+"_"+str(instance.id()),
                    str(self.model2.item(index).data(UIUtils.dataslot_language)),
                    str(self.model2.item(index).data(UIUtils.dataslot_annovalue)),
                    str(self.model2.item(index).data(UIUtils.dataslot_annovaluetype))
                ]
                QgsMessageLog.logMessage('Started task "{}"'.format(addarray), MESSAGE_CATEGORY, Qgis.Info)
                feature.setAttributes(addarray)
                QgsMessageLog.logMessage('Started task "{}"'.format(feature), MESSAGE_CATEGORY, Qgis.Info)
                feats.append(feature)
            findex+=1
        QgsMessageLog.logMessage('Started task "{}"'.format(feats), MESSAGE_CATEGORY, Qgis.Info)
        self.pr.addFeatures(feats)
        self.resultlayer.commitChanges()
        self.resultlayer.updateExtents()
        QgsMessageLog.logMessage('Started task "{}"'.format(self.resultlayer.featureCount()), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(len(self.resultlayer.fields())), MESSAGE_CATEGORY, Qgis.Info)
        #for index in range(0,self.model2.rowCount()):
        QgsProject.instance().addMapLayer(self.resultlayer)
        self.close()


    """Creating a specifically modified vector layer which could be converted to JSON-LD (W3C Web Annotation Data Model)"""
    def applyAnnotationToLayer(self):
        feature=QgsFeature()
        feature.setGeometry(self.selectiongeometry)
        index=0
        addarray=[
            str(self.model2.item(index).data(UIUtils.dataslot_target))+"_anno",
            str(self.model2.item(index).data(UIUtils.dataslot_annomotivation)),
            str(self.model2.item(index).data(UIUtils.dataslot_annotype)),
            str(self.model2.item(index).data(UIUtils.dataslot_annolicense)),
            str(self.model2.item(index).data(UIUtils.dataslot_annocreator)),
            str(self.model2.item(index).data(UIUtils.dataslot_relation)),
            str(self.model2.item(index).data(UIUtils.dataslot_target)),
            str(self.model2.item(index).data(UIUtils.dataslot_language)),
            str(self.model2.item(index).data(UIUtils.dataslot_annovalue)),
            str(self.model2.item(index).data(UIUtils.dataslot_annovaluetype))
        ]
        QgsMessageLog.logMessage('Started task "{}"'.format(addarray), MESSAGE_CATEGORY, Qgis.Info)
        feature.setAttributes(addarray)
        QgsMessageLog.logMessage('Started task "{}"'.format(feature), MESSAGE_CATEGORY, Qgis.Info)
        self.pr.addFeature(feature)
        self.resultlayer.updateExtents()
        QgsMessageLog.logMessage('Started task "{}"'.format(self.resultlayer.featureCount()), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(len(self.resultlayer.fields())), MESSAGE_CATEGORY, Qgis.Info)
        #for index in range(0,self.model2.rowCount()):
        QgsProject.instance().addMapLayer(self.resultlayer)
        self.close()




