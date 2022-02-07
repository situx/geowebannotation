from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand,QgsMapTool,QgsMapToolIdentifyFeature, QgsHighlight
from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.PyQt.QtGui import QColor, QKeySequence
from qgis.core import QgsProject, QgsPointXY, QgsRectangle, QgsWkbTypes,QgsCoordinateReferenceSystem, QgsCoordinateTransform
from math import sqrt,pi,cos,sin
from qgis.core import QgsApplication, QgsFeature
from ..dialogs.annotationdialog import AnnotateDialog
from qgis.core import Qgis,QgsTask, QgsMessageLog


MESSAGE_CATEGORY = 'GeoWebAnnotation'

class CircleMapTool(QgsMapTool):

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
        r = sqrt(center.sqrDist(edgePoint))
        self.rb.reset(QgsWkbTypes.PolygonGeometry)
        for itheta in range(N + 1):
            theta = itheta * (2.0 * pi / N)
            rb.addPoint(QgsPointXY(center.x() + r * cos(theta),
                               center.y() + r * sin(theta)))
        return
		
class PolygonMapTool(QgsMapTool):

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, iface):
        canvas = iface.mapCanvas()
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.status = 0
        self.layercoords=[]
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setColor(QColor(255, 0, 0, 100))
        self.rb2=QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)

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
            self.rb2.addPoint(self.toLayerCoordinates(self.iface.activeLayer(),e.pos()))
        else:
            if self.rb.numberOfVertices() > 2:
                self.status = 0
                self.selectionDone.emit()
                instancelist=[]
                rbgeom=self.rb.asGeometry()
                rb2geom = self.rb.asGeometry()
                layer = self.iface.activeLayer()
                QgsMessageLog.logMessage(str(rbgeom.asWkt()), MESSAGE_CATEGORY, Qgis.Info)
                QgsMessageLog.logMessage(str(rb2geom.asWkt()), MESSAGE_CATEGORY, Qgis.Info)
                QgsMessageLog.logMessage(str(layer), MESSAGE_CATEGORY, Qgis.Info)
                QgsMessageLog.logMessage(str(self.layercoords), MESSAGE_CATEGORY, Qgis.Info)
                #for lyr in self.iface.layerTreeView().activeLayer():
                for feat in self.iface.activeLayer().getFeatures():
                    geom = feat.geometry()
                    QgsMessageLog.logMessage(str(geom.asWkt())+" - "+str(rb2geom.asWkt()), MESSAGE_CATEGORY, Qgis.Info)
                    if rb2geom.intersects(geom):
                        QgsMessageLog.logMessage("Intersects: "+str(feat.id()), MESSAGE_CATEGORY,
                                                 Qgis.Info)
                        instancelist.append(feat)
                        #feat.append(feat.id())
                QgsMessageLog.logMessage(str(len(instancelist)), MESSAGE_CATEGORY, Qgis.Info)
                QgsMessageLog.logMessage(str(instancelist), MESSAGE_CATEGORY, Qgis.Info)
                annod=AnnotateDialog(instancelist,self.iface.activeLayer(),rb2geom)
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
        self.layercoords=[]
        self.rb.reset(True)

    def deactivate(self):
        self.rb.reset(True)
        self.layercoords = []
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
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setColor(QColor(255, 0, 0, 100))
        self.rb.setWidth(2)
        QgsMessageLog.logMessage("Initialized rectangle map tool", MESSAGE_CATEGORY, Qgis.Info)
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rb.reset(QgsWkbTypes.PolygonGeometry)

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        QgsMessageLog.logMessage((self.startPoint+" "+self.endPoint), MESSAGE_CATEGORY, Qgis.Info)
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
        self.rb.reset(QgsWkbTypes.PolygonGeometry)
        QgsMessageLog.logMessage("Show rect ", MESSAGE_CATEGORY, Qgis.Info)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return

        self.point1 = QgsPointXY(startPoint.x(), startPoint.y())
        self.point2 = QgsPointXY(startPoint.x(), endPoint.y())
        self.point3 = QgsPointXY(endPoint.x(), endPoint.y())
        self.point4 = QgsPointXY(endPoint.x(), startPoint.y())

        self.rb.addPoint(self.point1, False)
        self.rb.addPoint(self.point2, False)
        self.rb.addPoint(self.point3, False)
        # True to update canvas
        self.rb.addPoint(self.point4, True)
        self.rb.show()
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

    featureIdentified = pyqtSignal(QgsFeature)

    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.layer = self.iface.activeLayer()
        QgsMapToolIdentifyFeature.__init__(self, self.canvas)
        self.rb = QgsRubberBand(self.iface.mapCanvas())
        self.featureIdentified.connect(self.onIdentified)
        QgsMessageLog.logMessage("Initialized selection map tool!!! ", MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage(str(self.layer.name()), MESSAGE_CATEGORY, Qgis.Info)

    def onIdentified(self, feature):
        QgsMessageLog.logMessage("Found features " + str(feature), MESSAGE_CATEGORY, Qgis.Info)
        #found_features = self.identify(event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
        QgsMessageLog.logMessage("Found features " + str(feature), MESSAGE_CATEGORY, Qgis.Info)
        # self.layer.selectByIds([f.mFeature.id() for f in found_features], QgsVectorLayer.AddToSelection)
        if len(feature) > 0:
            self.featureHighlight = QgsHighlight(self.iface.mapCanvas(), self.referencingFeature.geometry(),
                                                 self.relation.referencingLayer())
            self.featureHighlight.setColor(QColor(255, 0, 0, 100))
            self.featureHighlight.show()
            self.featureIdentified.emit(feature)
        QgsMessageLog.logMessage("Canvas Pressed Event!!! ", MESSAGE_CATEGORY, Qgis.Info)

    def canvasReleaseEvent(self, e):
        self.status = 0
        self.point = self.toMapCoordinates(e.pos())
        QgsMessageLog.logMessage(str(e.pos())+" - "+str(self.point), MESSAGE_CATEGORY, Qgis.Info)

    def deactivate(self):
        self.layer.removeSelection()        


class LineMapTool(QgsMapTool):

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, iface):
        canvas = iface.mapCanvas()
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.status = 0
        self.point=None
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rb.setColor(QColor(255, 0, 0, 100))
        self.rb.setWidth(3)

    def canvasPressEvent(self, e):
        QgsMessageLog.logMessage("Canvas Released Event!!! ", MESSAGE_CATEGORY, Qgis.Info)
        if e.button() == Qt.LeftButton:
            self.point=self.toMapCoordinates(e.pos())
            self.rb.addPoint(self.point)
            QgsMessageLog.logMessage("Selected point: " + str(self.point), MESSAGE_CATEGORY, Qgis.Info)
        else:
            self.selectionDone.emit()

    def canvasMoveEvent(self, e):
        if self.rb.numberOfVertices() > 0 and self.status == 1:
            self.rb.removeLastPoint(0)
            self.rb.addPoint(self.toMapCoordinates(e.pos()))
        self.move.emit()

    def reset(self):
        self.status = 0
        self.rb.reset(QgsWkbTypes.LineGeometry)

    def deactivate(self):
        self.rb.reset(QgsWkbTypes.LineGeometry)
        QgsMapTool.deactivate(self)

class PointMapTool(QgsMapTool):

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, iface):
        canvas = iface.mapCanvas()
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.point=None
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        self.rb.setColor(QColor(255, 0, 0, 100))
        self.rb.setWidth(3)

    def canvasReleaseEvent(self, e):
        QgsMessageLog.logMessage("Canvas Released Event!!! ", MESSAGE_CATEGORY, Qgis.Info)
        if e.button() == Qt.LeftButton:
            self.point=self.toMapCoordinates(e.pos())
            self.rb.addPoint(self.point)
            QgsMessageLog.logMessage("Selected point: " + str(self.point), MESSAGE_CATEGORY, Qgis.Info)
            self.selectionDone.emit()

    def reset(self):
        self.rb.reset(QgsWkbTypes.PointGeometry)

    def deactivate(self):
        self.rb.reset(QgsWkbTypes.PointGeometry)
        QgsMapTool.deactivate(self)
