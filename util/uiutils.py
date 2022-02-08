from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt, QUrl, QEvent
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import QRegExp

class UIUtils:

    circleannoicon=QIcon(":/icons/resources/icons/circleanno.png")
    classicon = QIcon(":/icons/resources/icons/class.png")
    classlinkicon = QIcon(":/icons/resources/icons/classlink.png")
    searchclassicon = QIcon(":/icons/resources/icons/searchclass.png")
    objectpropertyicon = QIcon(":/icons/resources/icons/objectproperty.png")
    pointannoicon=QIcon(":/icons/resources/icons/pointanno.png")
    polygonannoicon=QIcon(":/icons/resources/icons/polygonanno.png")
    selectannoicon = QIcon(":/icons/resources/icons/selectanno.png")
    lineannoicon = QIcon(":/icons/resources/icons/lineanno.png")
    rectangleannoicon = QIcon(":/icons/resources/icons/rectangleanno.png")
    geowebannotationicon = QIcon(":/icons/resources/icons/icon.png")

    urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

    dataslot_conceptURI=256

    dataslot_annotype=257

    dataslot_annocontent=258

    dataslot_annomotivation=259

    dataslot_annolicense=260

    dataslot_annocreator=261

    dataslot_relation = 262

    dataslot_target = 263

    dataslot_language = 264

    dataslot_annovalue= 265

    dataslot_annovaluetype= 266

    @staticmethod
    def openListURL(item):
        concept = str(item.data(256))
        if concept.startswith("http"):
            url = QUrl(concept)
            QDesktopServices.openUrl(url)

    @staticmethod
    def copyClipBoard(item):
        concept = item.data(UIUtils.dataslot_conceptURI)
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(concept, mode=cb.Clipboard)

    @staticmethod
    def check_state(sender):
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)