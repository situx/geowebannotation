from qgis._gui import QgsMapToolIdentify
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand,QgsMapTool,QgsMapToolIdentifyFeature
from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.PyQt.QtGui import QColor, QKeySequence
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsPointXY, QgsRectangle, QgsWkbTypes,QgsCoordinateReferenceSystem, QgsCoordinateTransform
from math import sqrt,pi,cos,sin
from qgis.utils import iface
from qgis.core import QgsProject, QgsGeometry, QgsVectorLayer
from ..dialogs.webannotatedialog import AnnotateDialog


class CircleMapTool(QgsMapTool):
    '''Outil de sélection par cercle, tiré de selectPlusFr'''

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, iface, segments):
        canvas = iface.mapCanvas()
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.status = 0
        self.segments = segments
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setColor(QColor(255, 0, 0, 100))

    def canvasPressEvent(self, e):
        if not e.button() == Qt.LeftButton:
            return
        self.status = 1
        self.center = self.toMapCoordinates(e.pos())
        self.rbcircle(self.rb, self.center, self.center, self.segments)
        return

    def canvasMoveEvent(self, e):
        if not self.status == 1:
            return
        # construct a circle with N segments
        cp = self.toMapCoordinates(e.pos())
        self.rbcircle(self.rb, self.center, cp, self.segments)
        self.rb.show()
        self.move.emit()

    def canvasReleaseEvent(self, e):
        '''La sélection est faîte'''
        if not e.button() == Qt.LeftButton:
            return None
        self.status = 0
        if self.rb.numberOfVertices() > 3:
            self.selectionDone.emit()
        else:
            radius=2
			#, ok = QInputDialog.getDouble(self.iface.mainWindow(), tr('Radius'),tr('Give a radius in m:'), min=0)
            if radius > 0:
                cp = self.toMapCoordinates(e.pos())
                cp.setX(cp.x() + radius)
                self.rbcircle(self.rb, self.toMapCoordinates(
                    e.pos()), cp, self.segments)
                self.rb.show()
                self.selectionDone.emit()
        return None

    def reset(self):
        self.status = 0
        self.rb.reset(True)

    def deactivate(self):
        self.rb.reset(True)
        QgsMapTool.deactivate(self)
		
    def rbcircle(self,rb, center, edgePoint, N):
        '''Fonction qui affiche une rubberband sous forme de cercle'''
        r = sqrt(center.sqrDist(edgePoint))
        self.rb.reset(QgsWkbTypes.PolygonGeometry)
        for itheta in range(N + 1):
            theta = itheta * (2.0 * pi / N)
            rb.addPoint(QgsPointXY(center.x() + r * cos(theta),
                               center.y() + r * sin(theta)))
        return
		
class PolygonMapTool(QgsMapTool):
    '''Outil de sélection par polygone, tiré de selectPlusFr'''

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, iface):
        canvas = iface.mapCanvas()
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.status = 0
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setColor(QColor(255, 0, 0, 100))

    def keyPressEvent(self, e):
        if e.matches(QKeySequence.Undo):
            if self.rb.numberOfVertices() > 1:
                self.rb.removeLastPoint()

    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.status == 0:
                self.rb.reset(QgsWkbTypes.PolygonGeometry)
                self.status = 1
            self.rb.addPoint(self.toMapCoordinates(e.pos()))
        else:
            if self.rb.numberOfVertices() > 2:
                self.status = 0
                self.selectionDone.emit()
                instancelist=[]
                rbgeom=self.rb.asGeometry()
                msgBox=QMessageBox()
                msgBox.setText(str(rbgeom))
                msgBox.exec()
                layer = iface.activeLayer()
                for lyr in iface.layerTreeView().selectedLayers():
                    destCrs = QgsCoordinateReferenceSystem(lyr.crs())
                    #msgBox=QMessageBox()
                    #msgBox.setText(str(lyr.crs())+" "+str(layer.crs()))
                    #msgBox.exec();
                    tr = QgsCoordinateTransform(layer.crs(), QgsProject.instance().crs(), QgsProject.instance())
                    rbgeom.transform(tr)
                    selfeat=[]
                    for feat in lyr.getFeatures():
                        geom = feat.geometry()
                        #msgBox=QMessageBox()
                        #msgBox.setText(str(rbgeom)+" "+str(geom))
                        #msgBox.exec();
                        if rbgeom.intersects(geom):
                            msgBox=QMessageBox()
                            msgBox.setText(str("intersects"))
                            msgBox.exec()
                            instancelist.append(feat)
                            selfeat.append(feat.id())
                    msgBox=QMessageBox()
                    msgBox.setText(str(selfeat))
                    msgBox.exec()
                    #lyr.setSelectedFeatures(selfeat)
                annod=AnnotateDialog(instancelist)
                annod.exec()
            else:
                self.reset()
        return None

    def canvasMoveEvent(self, e):
        if self.rb.numberOfVertices() > 0 and self.status == 1:
            self.rb.removeLastPoint(0)
            self.rb.addPoint(self.toMapCoordinates(e.pos()))
        self.move.emit()
        return None

    def reset(self):
        self.status = 0
        self.rb.reset(True)

    def deactivate(self):
        self.rb.reset(True)
        QgsMapTool.deactivate(self)


class RectangleMapTool(QgsMapToolEmitPoint):

    rectangleCreated = pyqtSignal()
    deactivated = pyqtSignal()
	
    point1=""
    point2=""
    point3=""
    point4=""
    chosen=False

    def __init__(self, canvas):
        self.canvas = canvas.mapCanvas()
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(QColor(255, 0, 0, 100))
        self.rubberBand.setWidth(2)

        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True

        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        if self.rectangle() is not None:
            self.rectangleCreated.emit()

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return

        self.point1 = QgsPointXY(startPoint.x(), startPoint.y())
        self.point2 = QgsPointXY(startPoint.x(), endPoint.y())
        self.point3 = QgsPointXY(endPoint.x(), endPoint.y())
        self.point4 = QgsPointXY(endPoint.x(), startPoint.y())

        self.rubberBand.addPoint(self.point1, False)
        self.rubberBand.addPoint(self.point2, False)
        self.rubberBand.addPoint(self.point3, False)
        # True to update canvas
        self.rubberBand.addPoint(self.point4, True)
        self.rubberBand.show()
        chosen=True

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or \
                self.startPoint.y() == self.endPoint.y():
            return None

        return QgsRectangle(self.startPoint, self.endPoint)

    def setRectangle(self, rect):
        if rect == self.rectangle():
            return False

        if rect is None:
            self.reset()
        else:
            self.startPoint = QgsPointXY(rect.xMaximum(), rect.yMaximum())
            self.endPoint = QgsPointXY(rect.xMinimum(), rect.yMinimum())
            self.showRect(self.startPoint, self.endPoint)
        return True

    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.deactivated.emit()


class SelectMapTool(QgsMapToolIdentifyFeature):
    
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.layer = self.iface.activeLayer()
        QgsMapToolIdentifyFeature.__init__(self, self.canvas, self.layer)
        self.iface.currentLayerChanged.connect(self.active_changed)
        
    def active_changed(self, layer):
        self.layer.removeSelection()
        if isinstance(layer, QgsVectorLayer) and layer.isSpatial():
            self.layer = layer
            self.setLayer(self.layer)
            
    def canvasPressEvent(self, event):
        found_features = self.identify(event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
        self.layer.selectByIds([f.mFeature.id() for f in found_features], QgsVectorLayer.AddToSelection)
        msgBox=QMessageBox()
        msgBox.setWindowTitle("Test!")
        msgBox.setText(str(found_features))
        msgBox.exec()
        
    def deactivate(self):
        self.layer.removeSelection()        
        
class PointMapTool(QgsMapTool):
    '''Outil de sélection par polygone, tiré de selectPlusFr'''

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, iface):
        canvas = iface.mapCanvas()
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.status = 0
        self.point=None

    def keyPressEvent(self, e):
        print("test")

    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.point=self.toMapCoordinates(e.pos())
        else:
            self.selectionDone.emit()
        return None

    def canvasMoveEvent(self, e):
        self.move.emit()
        return None

    def reset(self):
        self.status = 0
        #self.rb.reset(True)

    def deactivate(self):
        #self.rb.reset(True)
        QgsMapTool.deactivate(self)
