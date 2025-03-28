from qgis.PyQt.QtWidgets import QStyle,QWidget,QMenu,QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtCore import QSortFilterProxyModel
from qgis.PyQt import uic
from qgis.core import QgsApplication, QgsMessageLog
import os

from ...dialogs.dataview.dataschemadialog import DataSchemaDialog
from ...dialogs.dataview.propertyschemadialog import PropertySchemaDialog
from ...util.sparqlutils import SPARQLUtils
from ...util.ui.uiutils import UIUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/clusterviewdialog.ui'))

MESSAGE_CATEGORY = 'ClusterviewDialog'

class ClusterViewDialog(QWidget, FORM_CLASS):

    def __init__(self,triplestoreconf,concept,label=""):
        super(QWidget, self).__init__()
        self.setupUi(self)
        self.label=label
        if self.label!=None and self.label!="":
            self.setWindowTitle("Related Concepts to " + str(label))
        else:
            self.setWindowTitle("Related Concepts to "+str(concept))
        self.triplestoreconf=triplestoreconf
        self.concept=concept
        self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation'))))
        self.tablemodel=QStandardItemModel()
        self.tablemodel.setHeaderData(0, Qt.Horizontal, "Ingoing Concept")
        self.tablemodel.setHeaderData(1, Qt.Horizontal, "Ingoing Relation")
        self.tablemodel.setHeaderData(2, Qt.Horizontal, "Outgoing Relation")
        self.tablemodel.setHeaderData(3, Qt.Horizontal, "Target Concept")
        self.tablemodel.insertRow(0)
        self.nodetype=SPARQLUtils.classnode
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_proxy_model.setSourceModel(self.tablemodel)
        self.filter_proxy_model.setFilterKeyColumn(3)
        self.tableView.setModel(self.filter_proxy_model)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.clusterView.hide()
        self.tableView.entered.connect(lambda modelindex: UIUtils.showTableURI(modelindex, self.tableView, self.statusBarLabel))
        self.tableView.doubleClicked.connect(self.showRelatedFromIndex)
        self.tableView.customContextMenuRequested.connect(self.onContext)
        self.filterTableEdit.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.filterTableComboBox.currentIndexChanged.connect(lambda: self.filter_proxy_model.setFilterKeyColumn(self.filterTableComboBox.currentIndex()))
        self.show()
        self.currentItem=None
        self.getRelatedClassStatistics()

    def showRelatedFromIndex(self):
        row=None
        col=None
        for idx in self.tableView.selectionModel().selectedIndexes():
            row = idx.row()
            col = idx.column()
        if row==None or col==None:
            return
        self.currentItem=self.tablemodel.item(row,col)
        if self.currentItem is not None:
            self.label=self.currentItem.text()
            self.showRelated(self.currentItem)

    def showRelated(self,item):
        self.concept=self.currentItem.data(UIUtils.dataslot_conceptURI)
        self.nodetype=self.currentItem.data(UIUtils.dataslot_nodetype)
        self.label=self.currentItem.data(0)
        self.tablemodel.clear()
        if self.label!=None and self.label!="":
            self.setWindowTitle("Related concept to " + str(self.label))
        else:
            self.setWindowTitle("Related concept to "+str(self.concept))
        self.getRelatedClassStatistics()


    def startSchemaDialog(self):
        if self.currentItem.data(UIUtils.dataslot_nodetype)==SPARQLUtils.datatypepropertynode or \
            self.currentItem.data(UIUtils.dataslot_nodetype)==SPARQLUtils.geodatatypepropertynode or \
            self.currentItem.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoobjectpropertynode or \
            self.currentItem.data(UIUtils.dataslot_nodetype) == SPARQLUtils.objectpropertynode:
            PropertySchemaDialog(
                self.currentItem.data(UIUtils.dataslot_conceptURI),
                self.currentItem.data(UIUtils.dataslot_nodetype),
                self.currentItem.data(0),
                self.triplestoreconf["resource"],
                self.triplestoreconf, self.triplestoreconf["prefixes"],
                "Property Schema View for " + SPARQLUtils.labelFromURI(str(self.currentItem.data(
                    UIUtils.dataslot_conceptURI)),
                    self.triplestoreconf["prefixesrev"] if "prefixesrev" in self.triplestoreconf else {}))
        else:
            DataSchemaDialog(
                self.currentItem.data(UIUtils.dataslot_conceptURI),
                self.currentItem.data(UIUtils.dataslot_nodetype),
                self.currentItem.data(0),
                self.triplestoreconf["resource"],
                self.triplestoreconf, self.triplestoreconf["prefixes"],
                "Data Schema View for " + SPARQLUtils.labelFromURI(str(self.currentItem.data(
                    UIUtils.dataslot_conceptURI)),
                    self.triplestoreconf["prefixesrev"] if "prefixesrev" in self.triplestoreconf else {}))


    def onContext(self, position):
        self.currentItem = self.tableView.indexAt(position)
        menu = QMenu("Menu", self)
        actionclip = QAction("Copy IRI to clipboard")
        actionclip.setIcon(UIUtils.classlinkicon)
        menu.addAction(actionclip)
        #actionclip.triggered.connect(lambda: ConceptContextMenu.copyClipBoard(self.currentItem))
        action = QAction("Open in Webbrowser")
        action.setIcon(UIUtils.geoclassicon)
        menu.addAction(action)
        action.triggered.connect(lambda: UIUtils.openListURL(self.currentItem))
        actiondataschema = QAction("Query data schema")
        actiondataschema.setIcon(UIUtils.classschemaicon)
        menu.addAction(actiondataschema)
        actiondataschema.triggered.connect(self.startSchemaDialog)
        actionshowrelated = QAction("Show related concepts")
        actionshowrelated.setIcon(UIUtils.countinstancesicon)
        menu.addAction(actionshowrelated)
        actionshowrelated.triggered.connect(self.showRelated)
        menu.exec(self.tableView.viewport().mapToGlobal(position))