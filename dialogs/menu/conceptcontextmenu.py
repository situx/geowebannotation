from qgis.PyQt.QtWidgets import QApplication, QMenu, QAction
from qgis.PyQt.QtGui import QDesktopServices
from qgis.core import (
    QgsApplication
)
from qgis.PyQt.QtCore import QUrl

from ..dataview.clusterviewdialog import ClusterViewDialog
from ...util.ui.uiutils import UIUtils
from ..dataview.dataschemadialog import DataSchemaDialog
from ...util.sparqlutils import SPARQLUtils

MESSAGE_CATEGORY = 'ContextMenu'

class ConceptContextMenu(QMenu):

    def __init__(self,dlg,triplestoreconf,prefixes,position,context,item,preferredlang=None,menu=None):
        super(ConceptContextMenu, self).__init__()
        self.triplestoreconf=triplestoreconf
        self.dlg=dlg
        self.preferredlang=preferredlang
        self.item=item
        self.prefixes=prefixes
        if menu==None:
            menu = QMenu("Menu", context)
        actionclip = QAction("Copy IRI to clipboard")
        if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.instancenode or item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoinstancenode:
            actionclip.setIcon(UIUtils.instancelinkicon)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.classnode or item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoclassnode:
            actionclip.setIcon(UIUtils.classlinkicon)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoclassnode:
            actionclip.setIcon(UIUtils.linkedgeoclassicon)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoinstancenode:
            actionclip.setIcon(UIUtils.linkedgeoinstanceicon)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.collectionclassnode:
            actionclip.setIcon(UIUtils.featurecollectionlinkicon)
        menu.addAction(actionclip)
        actionclip.triggered.connect(lambda: ConceptContextMenu.copyClipBoard(item))
        action = QAction("Open in Webbrowser")
        action.setIcon(UIUtils.geoclassicon)
        menu.addAction(action)
        action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(item.data(UIUtils.dataslot_conceptURI))))
        if item.data(UIUtils.dataslot_nodetype) != SPARQLUtils.instancenode and item.data(UIUtils.dataslot_nodetype) != SPARQLUtils.geoinstancenode\
                and item.data(UIUtils.dataslot_nodetype) != SPARQLUtils.linkedgeoinstancenode:
            actioninstancecount = QAction("Check instance count")
            actioninstancecount.setIcon(UIUtils.countinstancesicon)
            menu.addAction(actioninstancecount)
            actioninstancecount.triggered.connect(self.instanceCount)
            actiondataschema = QAction("Query data schema")
            if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.classnode:
                actiondataschema.setIcon(UIUtils.classschemaicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.collectionclassnode:
                actiondataschema.setIcon(UIUtils.featurecollectionschemaicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoclassnode:
                actiondataschema.setIcon(UIUtils.linkedgeoclassschemaicon)
            else:
                actiondataschema.setIcon(UIUtils.geoclassschemaicon)
            menu.addAction(actiondataschema)
            actiondataschema.triggered.connect(lambda: DataSchemaDialog(
                item.data(UIUtils.dataslot_conceptURI),
                item.data(UIUtils.dataslot_nodetype),
                item.text(),
                triplestoreconf["resource"],
                triplestoreconf, self.prefixes,
                "Data Schema View for " + SPARQLUtils.labelFromURI(str(item.data(UIUtils.dataslot_conceptURI)),
                                                                   triplestoreconf["prefixesrev"])
            ))
            actionrelgeo = QAction("Check related concepts")
            actionrelgeo.setIcon(UIUtils.countinstancesicon)
            menu.addAction(actionrelgeo)
            actionrelgeo.triggered.connect(self.relatedGeoConcepts)
            actionqueryinstances = QAction("Query all instances")
            actionqueryinstances.setIcon(UIUtils.queryinstancesicon)
            menu.addAction(actionqueryinstances)
            actionqueryinstances.triggered.connect(self.instanceList)
            if "subclassquery" in triplestoreconf:
                action2 = QAction("Load subclasses")
                action2.setIcon(UIUtils.subclassicon)
                menu.addAction(action2)
                action2.triggered.connect(self.loadSubClasses)
            #actionsubclassquery = QAction("Create subclass query")
            #actionsubclassquery.setIcon(UIUtils.subclassicon)
            #menu.addAction(actionsubclassquery)
            #actionsubclassquery.triggered.connect(self.dlg.subclassQuerySelectAction)
            actionquerysomeinstances = QAction("Add some instances as new layer")
            actionquerysomeinstances.setIcon(UIUtils.addfeaturecollectionicon)
            menu.addAction(actionquerysomeinstances)
            actionquerysomeinstances.triggered.connect(self.queryLimitedInstances)
            actionaddallInstancesAsLayer = QAction("Add all instances as new layer")
            actionaddallInstancesAsLayer.setIcon(UIUtils.addfeaturecollectionicon)
            menu.addAction(actionaddallInstancesAsLayer)
            actionaddallInstancesAsLayer.triggered.connect(lambda: self.dlg.dataAllInstancesAsLayer(False,None))
            actionallInstancesAsRDF = QAction("Instances as graph data")
            actionallInstancesAsRDF.setIcon(UIUtils.addfeaturecollectionicon)
            menu.addAction(actionallInstancesAsRDF)
            actionallInstancesAsRDF.triggered.connect(lambda: self.dlg.dataAllInstancesAsLayer(True,None))
        else:
            actiondataschemainstance = QAction("Query data")
            if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.instancenode:
                actiondataschemainstance.setIcon(UIUtils.instanceicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoinstancenode:
                actiondataschemainstance.setIcon(UIUtils.geoinstanceicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoinstancenode:
                actiondataschemainstance.setIcon(UIUtils.linkedgeoinstanceicon)
            menu.addAction(actiondataschemainstance)
            actiondataschemainstance.triggered.connect(self.dataInstanceView)
            actionaddInstanceAsLayer = QAction("Add instance as new layer")
            if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.instancenode:
                actionaddInstanceAsLayer.setIcon(UIUtils.addinstanceicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoinstancenode:
                actionaddInstanceAsLayer.setIcon(UIUtils.addgeoinstanceicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoinstancenode:
                actionaddInstanceAsLayer.setIcon(UIUtils.addinstanceicon)
            menu.addAction(actionaddInstanceAsLayer)
            actionaddInstanceAsLayer.triggered.connect(self.dlg.dataInstanceAsLayer)
            actionallInstanceAsRDF = QAction("Instance as graph data")
            actionallInstanceAsRDF.setIcon(UIUtils.addfeaturecollectionicon)
            menu.addAction(actionallInstanceAsRDF)
            actionallInstanceAsRDF.triggered.connect(lambda: self.dlg.dataAllInstancesAsLayer(True,None))
        if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoclassnode or item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoclassnode:
            actionquerybbox=QAction("Query layer in bbox")
            actionquerybbox.setIcon(UIUtils.bboxicon)
            actionquerybbox.triggered.connect(self.getBBOX)
            menu.addAction(actionquerybbox)
        if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoclassnode:
            actionquerylinkedgeoconcept = QAction("Query joined layer with linked geoconcept")
            actionquerylinkedgeoconcept.setIcon(UIUtils.linkedgeoclassicon)
            menu.addAction(actionquerylinkedgeoconcept)
            actionquerylinkedgeoconcept.triggered.connect(self.queryLinkedGeoConcept)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoinstancenode:
            actionquerylinkedgeoinstance = QAction("Query joined layer with linked geoinstance")
            actionquerylinkedgeoinstance.setIcon(UIUtils.linkedgeoinstanceicon)
            menu.addAction(actionquerylinkedgeoinstance)
            actionquerylinkedgeoinstance.triggered.connect(self.queryLinkedGeoInstance)
        #actionapplicablestyles = QAction("Find applicable styles")
        #menu.addAction(actionapplicablestyles)
        #actionapplicablestyles.triggered.connect(self.appStyles)
        menu.exec_(context.viewport().mapToGlobal(position))

    @staticmethod
    def createListContextMenu(item,menu=None):
        if menu==None:
            menu = QMenu("Menu")
        actionclip = QAction("Copy IRI to clipboard")
        menu.addAction(actionclip)
        actionclip.triggered.connect(lambda: ConceptContextMenu.copyClipBoard(item))
        action = QAction("Open in Webbrowser")
        menu.addAction(action)
        action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(item.data(UIUtils.dataslot_conceptURI))))
        return menu

    def appStyles(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(UIUtils.dataslot_conceptURI)
        label = self.currentContextModel.itemFromIndex(curindex).text()
        # self.dataschemaDialog = DataSchemaDialog(concept,label,self.triplestoreconf["resource"],self.triplestoreconf,self.prefixes,self.comboBox.currentIndex())
        # self.dataschemaDialog.setWindowTitle("Data Schema View for "+str(concept))
        # self.dataschemaDialog.exec_()


    def relatedGeoConcepts(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        label = self.item.text()
        ClusterViewDialog(self.triplestoreconf,concept,label)
        #if not label.endswith("]"):
        #    self.qtaskinstance = FindRelatedConceptQueryTask(
        #        "Getting related geo concepts for " + str(concept),
        #        self.triplestoreconf["resource"], self, concept,self.triplestoreconf)
        #    QgsApplication.taskManager().addTask(self.qtaskinstance)


    @staticmethod
    def copyClipBoard(item):
        concept = item.data(UIUtils.dataslot_conceptURI)
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(concept, mode=cb.Clipboard)
