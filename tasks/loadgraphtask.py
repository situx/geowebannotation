from time import sleep
from rdflib import *
import json
import requests
import urllib
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtCore import QSettings
from qgis.core import Qgis, QgsGeometry, QgsVectorLayer, QgsProject
from qgis.PyQt.QtWidgets import QCompleter,QMessageBox
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )

MESSAGE_CATEGORY = 'LoadGraphTask'

## Loads a graph from an RDF file either by providing an internet address or a file path.
class LoadGraphTask(QgsTask):

    def __init__(self, description, filename, loadgraphdlg,dlg,progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress=progress
        self.dlg=dlg
        self.graph=None
        self.geoconcepts=None
        self.exception=None
        self.filename=filename
        self.loadgraphdialog=loadgraphdlg
        self.geojson=None
        s = QSettings() #getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")

    def run(self):
        if self.proxyHost!=None and self.proxyHost!="" and self.proxyPort!=None and self.proxyPort!="":
            QgsMessageLog.logMessage('Proxy? '+str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()),MESSAGE_CATEGORY, Qgis.Info)
        try:
            if self.filename.startswith("http"):
                self.graph.load(self.filename)
            else:
                self.webannotationmodelToLayer(self.filename,None)
        except Exception as e:
            QgsMessageLog.logMessage('Failed "{}"'.format(str(e)),MESSAGE_CATEGORY, Qgis.Info)
            self.exception=str(e)
            return False
        return True

    def webannotationmodelToLayer(self,filepath,crsdef):
        layer=None
        print("loading json-ld")
        f = open(filepath)
        data = json.load(f)
        self.geojsonlayer={"type":"FeatureCollection","features":[]}
        for key in data:
            QgsMessageLog.logMessage(str(data[key]),MESSAGE_CATEGORY, Qgis.Info)
            if "body" in data[key] and "target" in data[key] and "selector" in data[key]["target"] and "type" in data[key]["target"]["selector"] and data[key]["target"]["selector"]["type"]=="GeoSelector" and data[key]["@context"]=="http://www.w3.org/ns/anno.jsonld":
                geom=QgsGeometry.fromWkt(str(data[key]["target"]["selector"]["value"]))
                feat={"type":"Feature","properties":{},"geometry":json.loads(geom.asJson())}
                if "id" in data[key]:
                    feat["id"]=data[key]["id"]
                else:
                    feat["id"]=key
                feat["properties"]["target"]=data[key]["target"]["source"]
                if "targetFeature" in data[key]["target"]["selector"]:
                    feat["properties"]["targetFeature"]=data[key]["target"]["selector"]["targetFeature"]
                if isinstance(data[key]["body"], list):
                    counter=1
                    for ann in data[key]["body"]:
                        if "value" in ann:
                            feat["properties"]["annotation"]=ann["value"]
                            feat["properties"]["annotationType"]=ann["type"]                            
                        else:
                            feat["properties"]["annotation"+counter]=data[key]["body"]
                            feat["properties"]["annotationType"]="URL"
                        counter=counter+1
                elif "value" in data[key]["body"]:
                    feat["properties"]["annotation"]=data[key]["body"]["value"]
                    feat["properties"]["annotationType"]=data[key]["body"]["type"]
                else:
                    feat["properties"]["annotation"]=data[key]["body"]
                    feat["properties"]["annotationType"]="URL"
                self.geojsonlayer["features"].append(feat)
        if self.loadgraphdialog.layerNameEdit.text()=="":
            self.vlayer = QgsVectorLayer(json.dumps(self.geojsonlayer, sort_keys=True, indent=4),"webannotation_"+filepath[filepath.rfind('/')+1:filepath.rfind('.')],"ogr")
        else:
            self.vlayer = QgsVectorLayer(json.dumps(self.geojsonlayer, sort_keys=True, indent=4),"webannotation_"+self.loadgraphdialog.layerNameEdit.text(),"ogr")
        f.close()
        return layer        

    def finished(self, result):
        msgBox=QMessageBox()
        msgBox.setText(str(self.geojsonlayer))
        msgBox.exec()
        if result==True:        
            QgsProject.instance().addMapLayer(self.vlayer)
            #self.dlg.geoClassListModel.clear()
            #self.dlg.comboBox.setCurrentIndex(0);
            #self.maindlg.currentgraph=self.graph
            #self.dlg.layercount.setText("["+str(len(self.geoconcepts))+"]")		
            #for geo in self.geoconcepts:
            #    item=QStandardItem()
            #    item.setData(geo,1)
            #    item.setText(geo[geo.rfind('/')+1:])
            #    self.dlg.geoClassListModel.appendRow(item)
            #comp=QCompleter(self.dlg.layerconcepts)
            #comp.setCompletionMode(QCompleter.PopupCompletion)
            #comp.setModel(self.dlg.layerconcepts.model())
            #self.dlg.layerconcepts.setCompleter(comp)
            #self.dlg.inp_sparql2.setPlainText(self.triplestoreconf[0]["querytemplate"][0]["query"].replace("%%concept%%",self.geoconcepts[0]))
            #self.dlg.inp_sparql2.columnvars={}
            #self.maindlg.loadedfromfile=True
            #self.maindlg.justloadingfromfile=False
            #self.loadgraphdlg.close()
            print("test")
        else:
            msgBox=QMessageBox()
            msgBox.setText(self.exception)
            msgBox.exec()
        self.progress.close()
