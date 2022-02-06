# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveAttribute
                                 A QGIS plugin
 This plugin saves the attributes of the selected vector layer as a CSV file.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-10-07
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Florian Thiery
        email                : rse@fthiery.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis._core import QgsWkbTypes
from qgis.core import QgsProject, Qgis
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand,QgsMapTool,QgsMapToolIdentifyFeature, QgsHighlight

# Initialize Qt resources from file resources.py
import os.path
import sys
from .resources import *
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "dependencies")))
import uuid
import re
import json
import urllib.parse
from rdflib import *
from SPARQLWrapper import SPARQLWrapper, JSON, POST
# Import the code for the dialog
from .util.uiutils import UIUtils
from .dialogs.geowebannotation_dialog import GeoWebAnnotationDialog
from .util.geowebannotationtool import CircleMapTool, LineMapTool
from .util.geowebannotationtool import RectangleMapTool
from .util.geowebannotationtool import PolygonMapTool
from .util.geowebannotationtool import PointMapTool
from .util.geowebannotationtool import SelectMapTool
from .dialogs.loadgraphdialog import LoadGraphDialog
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'GeoWebAnnotation'

class GeoWebAnnotation:
    """QGIS Plugin Implementation."""

    layers=None
    
    currentLayer=None
    
    exportNameSpace=None

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoWebAnnotation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
        self.actions = []
        self.menu = self.tr(u'&GeoWebAnnotation')
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        return QCoreApplication.translate('GeoWebAnnotation', message)


    def create_annotation_layer(self,layername):
        QgsMessageLog.logMessage("Create annotation layer", MESSAGE_CATEGORY, Qgis.Info)
          
    def export_annotation_layer(self,layername):
        QgsMessageLog.logMessage("Export annotation layer", MESSAGE_CATEGORY, Qgis.Info)

    def choose_point_mapping_tool(self):
        QgsMessageLog.logMessage("Selected point mapping tool", MESSAGE_CATEGORY, Qgis.Info)
        self.iface.mapCanvas().setMapTool( PointMapTool(self.iface) )

    def choose_line_mapping_tool(self):
        QgsMessageLog.logMessage("Selected line mapping tool", MESSAGE_CATEGORY, Qgis.Info)
        self.iface.mapCanvas().setMapTool( LineMapTool(self.iface) )

    def choose_polygon_mapping_tool(self):
        QgsMessageLog.logMessage("Selected polygon mapping tool", MESSAGE_CATEGORY, Qgis.Info)
        self.iface.mapCanvas().setMapTool( PolygonMapTool(self.iface) )

    def choose_circle_mapping_tool(self):
        QgsMessageLog.logMessage("Selected circle mapping tool", MESSAGE_CATEGORY, Qgis.Info)
        self.iface.mapCanvas().setMapTool( CircleMapTool(self.iface,1) )

    def choose_rectangle_mapping_tool(self):
        QgsMessageLog.logMessage("Selected rectangle mapping tool", MESSAGE_CATEGORY, Qgis.Info)
        self.iface.mapCanvas().setMapTool( RectangleMapTool(self.iface.mapCanvas()) )

    def choose_select_mapping_tool(self):
        QgsMessageLog.logMessage("Selected select mapping tool", MESSAGE_CATEGORY, Qgis.Info)
        idtool=QgsMapToolIdentifyFeature(self.iface.mapCanvas())
        idtool.setLayer(self.iface.activeLayer())
        QgsMessageLog.logMessage(str(self.iface.activeLayer().name()), MESSAGE_CATEGORY, Qgis.Info)
        idtool.featureIdentified.connect(self.onFeatureIdentified)
        self.iface.mapCanvas().setMapTool(idtool)

    def onFeatureIdentified(self,feature):
        QgsMessageLog.logMessage(str(feature), MESSAGE_CATEGORY, Qgis.Info)
        self.featureHighlight = QgsHighlight(self.iface.mapCanvas(), feature.geometry(),
                                             self.iface.activeLayer())
        self.featureHighlight.setColor(QColor(255, 0, 0, 100))
        self.featureHighlight.show()


    def add_action(
        self,
        icon,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        self.add_action(
            UIUtils.geowebannotationicon,
            text=self.tr(u'GeoWebAnnotation'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.add_action(
            UIUtils.polygonannoicon,
            text=self.tr(u'PolygonMapTool'),
            callback=self.choose_polygon_mapping_tool,
            parent=self.iface.mainWindow())

        self.add_action(
            UIUtils.lineannoicon,
            text=self.tr(u'LineMapTool'),
            callback=self.choose_line_mapping_tool,
            parent=self.iface.mainWindow())

        self.add_action(
            UIUtils.pointannoicon,
            text=self.tr(u'PointMapTool'),
            callback=self.choose_point_mapping_tool,
            parent=self.iface.mainWindow())

        self.add_action(
            UIUtils.rectangleannoicon,
            text=self.tr(u'RectangleMapTool'),
            callback=self.choose_rectangle_mapping_tool,
            parent=self.iface.mainWindow())

        self.add_action(
            UIUtils.selectannoicon,
            text=self.tr(u'SelectMapTool'),
            callback=self.choose_select_mapping_tool,
            parent=self.iface.mainWindow())
        
        self.add_action(
            UIUtils.circleannoicon,
            text=self.tr(u'CircleMapTool'),
            callback=self.choose_circle_mapping_tool,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&GeoWebAnnotation'),
                action)
            self.iface.removeToolBarIcon(action)

    def saveLayer(self):
        if self.dlg.exportFormatComboBox.currentText()=="GeoJSON-LD":
            self.exportLayerAsGeoJSONLD()
        elif self.dlg.exportFormatComboBox.currentText()=="JSON-LD":
            self.exportLayer(None, None, None, None, None, None, False)
        else:
            self.exportLayer(None, None, None, None, None, None, False)

    ## Creates the export layer dialog for exporting layers as TTL.
    #  @param self The object pointer.
    def exportLayer(self,urilist=None,classurilist=None,includelist=None,proptypelist=None,valuemappings=None,valuequeries=None,exportToTripleStore=False):
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.dlg.selectAnnotationLayerComboBox.currentText()
        layers = QgsProject.instance().mapLayersByName(selectedLayerIndex)
        layer=layers[0]
        if exportToTripleStore:
            ttlstring=self.layerToTTLString(layer,urilist,classurilist,includelist,proptypelist,valuemappings,valuequeries)
        else:
            filename, _filter = QFileDialog.getSaveFileName(
                self.dlg, "Select   output file ","", "Linked Data (*.ttl *.n3 *.nt)",)
            if filename=="":
                return
            ttlstring=self.layerToTTLString(layer,urilist,classurilist,includelist,proptypelist,valuemappings,valuequeries)
            g=Graph()
            g.parse(data=ttlstring, format="ttl")
            splitted=filename.split(".")
            exportNameSpace=""
            exportSetClass=""
            with open(filename, 'w') as output_file:
                output_file.write(g.serialize(format=splitted[len(splitted)-1]).decode("utf-8"))
                #iface.messageBar().pushMessage("export layer successfully!", "OK", level=Qgis.Success)

    ## Converts a QGIS layer to TTL with or withour a given column mapping.
    #  @param self The object pointer. 
    #  @param layer The layer to convert. 
    def layerToTTLString(self,layer,urilist=None,classurilist=None,includelist=None,proptypelist=None,valuemappings=None,valuequeries=None):
        fieldnames = [field.name() for field in layer.fields()]
        ttlstring="<http://www.opengis.net/ont/geosparql#Feature> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n"
        ttlstring+="<http://www.opengis.net/ont/geosparql#SpatialObject> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n"
        ttlstring+="<http://www.opengis.net/ont/geosparql#Geometry> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n"
        ttlstring+="<http://www.opengis.net/ont/geosparql#hasGeometry> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n"
        ttlstring+="<http://www.opengis.net/ont/geosparql#asWKT> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n"
        ttlstring+="<http://www.opengis.net/ont/geosparql#Feature> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#SpatialObject> .\n"
        ttlstring+="<http://www.opengis.net/ont/geosparql#Geometry> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#SpatialObject> .\n"
        first=0
        if self.exportNameSpace==None or self.exportNameSpace=="":
            namespace="http://www.github.com/sparqlunicorn#"
        else:
            namespace=self.exportNameSpace
        if self.exportIdCol=="":
            idcol="id"
        else:
            idcol=self.exportIdCol
        classcol="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        curid=""
        if self.exportSetClass==None or self.exportSetClass=="":
            curclassid=namespace+str(uuid.uuid4())
        elif self.exportSetClass.startswith("http"):
            curclassid=self.exportSetClass
        else:
            curclassid=urllib.parse.quote(self.exportSetClass)
        for f in layer.getFeatures():
            geom = f.geometry()
            if not idcol in fieldnames:
                curid=namespace+str(uuid.uuid4())
            elif not str(f[idcol]).startswith("http"):
                curid=namespace+str(f[idcol])
            else:
                curid=f[idcol]
            if not classcol in fieldnames:
                ttlstring+="<"+str(curid)+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <"+curclassid+"> .\n"
                if first==0:
                    ttlstring+="<"+str(curclassid)+"> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Feature> .\n"
                    ttlstring+="<"+str(curclassid)+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n"
            ttlstring+="<"+str(curid)+"> <http://www.opengis.net/ont/geosparql#hasGeometry> <"+curid+"_geom> .\n"
            ttlstring+="<"+str(curid)+"_geom> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/geosparql#"+QgsWkbTypes.displayString(geom.wkbType())+"> .\n"
            ttlstring+="<http://www.opengis.net/ont/geosparql#"+QgsWkbTypes.displayString(geom.wkbType())+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n"
            ttlstring+="<http://www.opengis.net/ont/geosparql#"+QgsWkbTypes.displayString(geom.wkbType())+"> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Geometry> .\n"
            ttlstring+="<"+str(curid)+"_geom> <http://www.opengis.net/ont/geosparql#asWKT> \""+geom.asWkt()+"\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> .\n"
            fieldcounter=-1
            for propp in fieldnames:
                fieldcounter+=1
                #if fieldcounter>=len(fieldnames):
                #    fieldcounter=0
                if includelist!=None and fieldcounter<len(includelist) and includelist[fieldcounter]==False:
                    continue
                prop=propp    
                print(str(fieldcounter))
                print(str(urilist)+"\n")
                print(str(classurilist)+"\n")
                print(str(includelist)+"\n")
                if urilist!=None and urilist[fieldcounter]!="":
                    print(urilist)
                    if not urilist[fieldcounter].startswith("http"):
                        print("Does not start with http")
                        prop=urllib.parse.quote(urilist[fieldcounter])
                    else:
                        prop=urilist[fieldcounter]
                    print("New Prop from list: "+str(prop))
                if prop=="id":
                    continue
                if not prop.startswith("http"):
                    prop=namespace+prop
                if prop=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and "http" in str(f[propp]):
                    ttlstring+="<"+str(f[propp])+"> <"+str(prop)+"> <http://www.w3.org/2002/07/owl#Class> .\n"
                    ttlstring+="<"+str(f[propp])+"> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Feature> .\n"
                elif prop=="http://www.w3.org/2000/01/rdf-schema#label" or prop=="http://www.w3.org/2000/01/rdf-schema#comment" or (proptypelist!=None and proptypelist[fieldcounter]=="AnnotationProperty"):
                    ttlstring+="<"+curid+"> <"+prop+"> \""+str(f[propp]).replace('"','\\"')+"\"^^<http://www.w3.org/2001/XMLSchema#string> .\n"
                    if first<10:
                        ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#AnnotationProperty> .\n" 
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n"  						
                elif not f[propp] or f[propp]==None or f[propp]=="":
                    continue
                elif proptypelist!=None and proptypelist[fieldcounter]=="SubClass":
                    ttlstring+="<"+curid+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <"+str(f[propp])+"> .\n"
                    ttlstring+="<"+curid+"> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <"+curclassid+"> .\n"
                    if first<10:
                        ttlstring+="<"+str(f[propp])+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n" 
                elif valuequeries!=None and propp in valuequeries:
                    ttlstring+=""
                    sparql = SPARQLWrapper(valuequeries[propp][1], agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                    sparql.setQuery(valuequeries[propp][0].replace("%%"+propp+"%%","\""+str(f[propp])+"\""))
                    sparql.setMethod(POST)
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    ttlstring+="<"+curid+"> <"+prop+"> <"+results["results"]["bindings"][0]["item"]["value"]+"> ."
                    if first<10:
                        ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n"
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n"  
                        if classurilist[fieldcounter]!="":
                             ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <"+classurilist[fieldcounter]+"> .\n"
                elif valuemappings!=None and propp in valuemappings and f[propp] in self.valuemappings[propp]:
                    ttlstring+="<"+curid+"> <"+prop+"> <"+str(self.valuemappings[propp][f[propp]])+"> .\n"
                    if first<10:
                        ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n"
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n"  
                        if classurilist[fieldcounter]!="":
                             ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <"+classurilist[fieldcounter]+"> .\n"
                elif "http" in str(f[propp]) or (proptypelist!=None and proptypelist[fieldcounter]=="ObjectProperty"):
                    ttlstring+="<"+curid+"> <"+prop+"> <"+str(f[propp])+"> .\n"
                    if first<10:
                        ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n"
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n"  
                        if classurilist!=None and fieldcounter<len(classurilist) and classurilist[fieldcounter]!="":
                             ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <"+classurilist[fieldcounter]+"> .\n"
                elif re.match(r'^-?\d+$', str(f[propp])):
                    ttlstring+="<"+curid+"> <"+prop+"> \""+str(f[propp])+"\"^^<http://www.w3.org/2001/XMLSchema#integer> .\n"
                    if first<10:
                        ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n"
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n" 
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#integer> .\n" 
                elif re.match(r'^-?\d+(?:\.\d+)?$', str(f[propp])):
                    ttlstring+="<"+curid+"> <"+prop+"> \""+str(f[propp])+"\"^^<http://www.w3.org/2001/XMLSchema#double> .\n"
                    if first:
                        ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n"
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n" 
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#double> .\n" 
                else:
                    ttlstring+="<"+curid+"> <"+prop+"> \""+str(f[propp]).replace('"','\\"')+"\"^^<http://www.w3.org/2001/XMLSchema#string> .\n"
                    if first<10:
                        ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n"
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n" 
                        ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#string> .\n" 
            if first<10:
                first=first+1
        return ttlstring


    def exportLayerAsGeoJSONLD(self):
        filename, _filter = QFileDialog.getSaveFileName(self.dlg, "Select   output file ","", "GeoJSON-LD (*.json)",)
        if filename=="":
            return
        context={
    "geojson": "https://purl.org/geojson/vocab#",
    "Feature": "geojson:Feature",
    "FeatureCollection": "geojson:FeatureCollection",
    "GeometryCollection": "geojson:GeometryCollection",
    "LineString": "geojson:LineString",
    "MultiLineString": "geojson:MultiLineString",
    "MultiPoint": "geojson:MultiPoint",
    "MultiPolygon": "geojson:MultiPolygon",
    "Point": "geojson:Point",
    "Polygon": "geojson:Polygon",
    "bbox": {
      "@container": "@list",
      "@id": "geojson:bbox"
    },
    "coordinates": {
      "@container": "@list",
      "@id": "geojson:coordinates"
    },
    "features": {
      "@container": "@set",
      "@id": "geojson:features"
    },
    "geometry": "geojson:geometry",
    "id": "@id",
    "properties": "geojson:properties",
    "type": "@type",
    "description": "http://purl.org/dc/terms/description",
    "title": "http://purl.org/dc/terms/title"
  }
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.dlg.selectAnnotationLayerComboBox.currentText()
        layers = QgsProject.instance().mapLayersByName(selectedLayerIndex)
        layer=layers[0]
        fieldnames = [field.name() for field in layer.fields()]
        currentgeo={}
        geos=[]
        for f in layer.getFeatures():
            geom = f.geometry()
            currentgeo={'id':'','geometry':json.loads(geom.asJson()),'properties':{}}
            for prop in fieldnames:
                if prop=="id":
                    currentgeo["id"]=f[prop]
                else:
                    currentgeo["properties"][prop]=f[prop]
            geos.append(currentgeo)
        featurecollection={"@context":context, "type":"FeatureCollection", "@id":"http://example.com/collections/1", "features": geos }
        f = open(filename, "w")
        f.write(json.dumps(featurecollection))
        f.close()
        return


        
    def loadWebAnnotationLayer(self):
        print("load layer")
        #vlayer = QgsVectorLayer(json.dumps(geojson, sort_keys=True, indent=4),"unicorn_"+self.dlg.inp_label.text(),"ogr")
        
    ## 
    #  @brief Creates a What To Enrich dialog with parameters given.
    #  
    #  @param self The object pointer
    def buildLoadGraphDialog(self):	
        self.searchTripleStoreDialog = LoadGraphDialog(None,self.dlg,self)	
        self.searchTripleStoreDialog.setWindowTitle("Load Graph")	
        self.searchTripleStoreDialog.exec_()


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = GeoWebAnnotationDialog()

        # Fetch the currently loaded layers
        layers = QgsProject.instance().layerTreeRoot().children()
        # Clear the contents of the comboBox from previous runs
        self.dlg.layerToAnnotateComboBox.clear()
        # Populate the comboBox with names of all the loaded layers
        layerlist=[]
        for layer in layers:
            if not "webannotation" in layer.name():
                layerlist.append(layer.name())
        self.dlg.layerToAnnotateComboBox.addItems(layerlist)
        annotationlayers=[]
        for layer in layers:
            if "webannotation" in layer.name():
                annotationlayers.append(layer.name())
        self.dlg.selectAnnotationLayerComboBox.addItems(annotationlayers)    
        self.dlg.loadAnnotationLayerButton.clicked.connect(self.buildLoadGraphDialog)
        self.dlg.saveLayerButton.clicked.connect(self.saveLayer)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
