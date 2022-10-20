from maya import cmds
from maya import OpenMayaUI as omui
import logging
import Qt
from PySide2 import QtWidgets, QtCore, QtGui  # TODO change to Qt later
from importlib import reload
import main
# from autoMat.src import main
reload(main)  # TODO remove later only for WIP with maya

logging.basicConfig()
logger = logging.getLogger('AutoMat')
logger.setLevel(logging.DEBUG)

if Qt.__binding__ == 'PySide':
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
    logger.debug('Using PySide with shiboken')
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal
    logger.debug('Using Qt with sip')
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal
    logger.debug('Using PySide2 with shiboken')


def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(int(win), QtWidgets.QMainWindow)
    return ptr


def getDock(name: str = 'AutoMat'):
    deleteDock()
    ctrl = cmds.workspaceControl(name, label="AutoMat", vis=True)
    qtCtrl = omui.MQtUtil.findControl(ctrl)
    ptr = wrapInstance(int(qtCtrl), QtWidgets.QWidget)
    return ptr


def deleteDock(name: str = 'AutoMat'):
    if cmds.workspaceControl(name, query=True, exists=True):
        cmds.deleteUI(name)


class AutoMatUI(QtWidgets.QWidget):

    def __init__(self, dock: bool = False):
        if dock:
            parent = getDock()
        else:
            deleteDock()

            try:
                cmds.deleteUI('AutoMat')
            except:
                logger.debug('No previous UI exists')

            parent = QtWidgets.QDialog(parent=getMayaMainWindow())
            parent.setObjectName('AutoMat')
            parent.setWindowTitle('AutoMat')
            layout = QtWidgets.QVBoxLayout(parent)

        super(AutoMatUI, self).__init__(parent=parent)
        """
        This class holds all necessary variables and methods to build, populate and update the UI.
        """

        # TODO setup window size relativ to screen size
        self.autoMat = main.autoMat()
        self.triplanar = False
        self.showInVP = True
        self.buildUI()
        self.populate()

        self.parent().layout().addWidget(self)
        if not dock:
            parent.show()

    def buildUI(self):
        """
        Creates all GUI elemnts and links each signal to their respective methods
        """
        # main vertical UI layout
        layout = QtWidgets.QVBoxLayout(self)

        # top UI bar as horizontal layout
        self.loadNameLabel = QtWidgets.QLabel("Choose a Texture Folder")
        self.loadNameLabel.setStyleSheet("font-size: 11pt")
        self.loadNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.loadNameLabel)

        # UI for reading folders
        loadWidget = QtWidgets.QWidget()
        loadLayout = QtWidgets.QHBoxLayout(loadWidget)
        layout.addWidget(loadWidget)

        # reset button
        resetBtn = QtWidgets.QPushButton('Reset List')
        resetBtn.setStyleSheet("font-size: 11pt")
        resetBtn.setToolTip("Delete texture list")
        resetBtn.clicked.connect(self.clearList)
        loadLayout.addWidget(resetBtn)

        # input field
        self.loadNameField = QtWidgets.QLineEdit()
        self.loadNameField.insert('No texture folder selected')
        self.loadNameField.setStyleSheet("font-size: 11pt")
        self.loadNameField.setToolTip("Path to texture folder")
        self.loadNameField.textChanged.connect(self.updatePath)
        loadLayout.addWidget(self.loadNameField)

        # select button
        loadBtn = QtWidgets.QPushButton('Select')
        loadBtn.setStyleSheet("font-size: 11pt")
        loadBtn.setToolTip("Open file dialog and choose folder")
        loadBtn.clicked.connect(self.chooseDirectory)
        loadLayout.addWidget(loadBtn)

        # list widget
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setToolTip("List of detected textures")
        layout.addWidget(self.listWidget)

        # display options layout
        displayOptionsWidget = QtWidgets.QWidget()
        displayOptionsLayout = QtWidgets.QHBoxLayout(displayOptionsWidget)
        layout.addWidget(displayOptionsWidget)

        # display in viewport checkbox
        vpCompCheck = QtWidgets.QCheckBox("Display in Viewport")
        vpCompCheck.setChecked(True)
        vpCompCheck.setStyleSheet("font-size: 12pt")
        vpCompCheck.setToolTip(
            "Setup materials to show viewport previews (Wont work with udims)")
        vpCompCheck.stateChanged.connect(self.dispVP)
        displayOptionsLayout.addWidget(vpCompCheck)

        # colorspace combobox
        self.csDropdown = QtWidgets.QComboBox()
        self.csDropdown.addItem("Maya ACES")
        self.csDropdown.addItem("General ACES")
        self.csDropdown.setStyleSheet("font-size: 11pt")
        self.csDropdown.setToolTip("Select a colorspace for image nodes")
        self.csDropdown.currentIndexChanged.connect(self.switchCS)
        displayOptionsLayout.addWidget(self.csDropdown)

        # shader details horizontal
        shaderDetailsWidget = QtWidgets.QWidget()
        shaderDetailsLayout = QtWidgets.QHBoxLayout(shaderDetailsWidget)
        layout.addWidget(shaderDetailsWidget)

        # displacement options vertical
        dispOptionsWidget = QtWidgets.QWidget()
        dispOptionsLayout = QtWidgets.QVBoxLayout(dispOptionsWidget)
        shaderDetailsLayout.addWidget(dispOptionsWidget)

        # vertical label fields for displacement
        dispLabel = QtWidgets.QLabel("Displacement")
        dispLabel.setStyleSheet("font-size: 12pt")
        dispLabel.setToolTip(
            "Displacement options in each objects shape node")
        dispOptionsLayout.addWidget(dispLabel)

        subdivLabel = QtWidgets.QLabel("Subdivisions")
        subdivLabel.setStyleSheet("font-size: 11pt")
        subdivLabel.setToolTip(
            "Number of subdivisions to use for displaced geometry")
        dispOptionsLayout.addWidget(subdivLabel)

        heightLabel = QtWidgets.QLabel("Height")
        heightLabel.setStyleSheet("font-size: 11pt")
        heightLabel.setToolTip(
            "Displacement strength, usualy pretty low values")
        dispOptionsLayout.addWidget(heightLabel)

        # vertical edit fields for displacement
        dispEditWidget = QtWidgets.QWidget()
        dispEditLayout = QtWidgets.QVBoxLayout(dispEditWidget)
        shaderDetailsLayout.addWidget(dispEditWidget)

        dispPH = QtWidgets.QLabel("")
        dispPH.setStyleSheet("font-size: 13pt")
        dispEditLayout.addWidget(dispPH)

        self.subdivLineEdit = QtWidgets.QLineEdit()
        self.subdivLineEdit.insert('3')
        self.subdivLineEdit.setStyleSheet("font-size: 10pt")
        self.subdivLineEdit.textChanged.connect(self.setDispSubdiv)
        dispEditLayout.addWidget(self.subdivLineEdit)

        self.heightLineEdit = QtWidgets.QLineEdit()
        self.heightLineEdit.insert('0.05')
        self.heightLineEdit.setStyleSheet("font-size: 10pt")
        dispEditLayout.addWidget(self.heightLineEdit)

        # triplanar options vertical
        tripOptionsWidget = QtWidgets.QWidget()
        tripOptionsLayout = QtWidgets.QVBoxLayout(tripOptionsWidget)
        shaderDetailsLayout.addWidget(tripOptionsWidget)

        # vertical label fields for triplanar
        tripLabel = QtWidgets.QLabel("Triplanar")
        tripLabel.setStyleSheet("font-size: 12pt")
        tripLabel.setToolTip("Use triplanar projection for each texture")
        tripOptionsLayout.addWidget(tripLabel)

        scaleLabel = QtWidgets.QLabel("Scale")
        scaleLabel.setStyleSheet("font-size: 11pt")
        scaleLabel.setToolTip("Texture scale to project on geometry")
        tripOptionsLayout.addWidget(scaleLabel)

        blendLabel = QtWidgets.QLabel("Blend")
        blendLabel.setStyleSheet("font-size: 11pt")
        blendLabel.setToolTip("Blend strength between projected textures")
        tripOptionsLayout.addWidget(blendLabel)

        # vertical edit fields for triplanar
        tripEditWidget = QtWidgets.QWidget()
        tripEditLayout = QtWidgets.QVBoxLayout(tripEditWidget)
        shaderDetailsLayout.addWidget(tripEditWidget)

        enableCheck = QtWidgets.QCheckBox()
        enableCheck.setStyleSheet("font-size: 13pt")
        enableCheck.stateChanged.connect(self.switchTriPlanar)
        tripEditLayout.addWidget(enableCheck)

        # disabled if checkbox not ticked
        self.scaleLineEdit = QtWidgets.QLineEdit()
        self.scaleLineEdit.insert('0.65')
        self.scaleLineEdit.setStyleSheet("font-size: 10pt")
        self.scaleLineEdit.setEnabled(False)
        self.scaleLineEdit.textChanged.connect(self.setTripScale)
        tripEditLayout.addWidget(self.scaleLineEdit)

        self.blendLineEdit = QtWidgets.QLineEdit()
        self.blendLineEdit.insert('1.0')
        self.blendLineEdit.setStyleSheet("font-size: 10pt")
        self.blendLineEdit.setEnabled(False)
        self.blendLineEdit.textChanged.connect(self.setTripBlend)
        tripEditLayout.addWidget(self.blendLineEdit)

        # horizontal button layout
        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout(btnWidget)
        layout.addWidget(btnWidget)

        importBtn = QtWidgets.QPushButton('Setup Materials')
        importBtn.setStyleSheet("font-size: 11pt")
        importBtn.setToolTip("Setup materials and assign to preview spheres")
        importBtn.clicked.connect(self.executeScript)
        btnLayout.addWidget(importBtn)

        matResetBtn = QtWidgets.QPushButton('Remove Materials')
        matResetBtn.setStyleSheet("font-size: 11pt")
        matResetBtn.setToolTip(
            "remove all created materials and their preview spheres")
        matResetBtn.clicked.connect(self.resetMats)
        btnLayout.addWidget(matResetBtn)

        closeBtn = QtWidgets.QPushButton('Close')
        closeBtn.setStyleSheet("font-size: 11pt")
        closeBtn.setToolTip("Close UI Window")
        closeBtn.clicked.connect(self.closeUI)
        btnLayout.addWidget(closeBtn)

        # status label
        statusWidget = QtWidgets.QWidget()
        statusLayout = QtWidgets.QHBoxLayout(statusWidget)
        layout.addWidget(statusWidget)

        self.statusLabel = QtWidgets.QLabel()
        statusLayout.addWidget(self.statusLabel)

    def populate(self):
        """
        This Methods assigns all given data to the UI elements
        """
        self.loadNameField.setText(self.autoMat.dataPath)

        # add dictionary values to list widget
        self.listWidget.clear()
        for keys, values in self.autoMat.dataDict.items():
            self.listWidget.addItem(keys)
            self.listWidget.addItems(values)

        self.listWidget.setStyleSheet("font-size: 11pt")

        # TODO add more status notes
        folderCount = len(self.autoMat.dataDict.keys())
        if folderCount == 1:
            self.statusLabel.setText(
                f"Status:  Found {folderCount} texture folder.")
        else:
            self.statusLabel.setText(
                f"Status: Found {folderCount} texture folders.")

        self.statusLabel.setStyleSheet("font-size: 13pt")

    def chooseDirectory(self):
        """
        This Opens a fie dialog and assigns the selected directory to the path to the autoMats instance dataPath variable
        """
        dialog = QtWidgets.QFileDialog(self)
        dialog.setDirectory(self.autoMat.dataPath)
        dialog.setWindowTitle('Choose texture folder')
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        self.autoMat.dataPath = dialog.getExistingDirectory()
        self.autoMat.findFiles()
        self.populate()

    def updatePath(self):
        self.autoMat.dataPath = self.loadNameField.text()
        self.autoMat.findFiles()
        self.populate()

    def setDispSubdiv(self):
        self.autoMat.dispSubdivs = int(self.subdivLineEdit.text())

    def setDisplacementHeight(self):
        self.autoMat.dispHeight = float(self.heightLineEdit.text())

    def setTripScale(self):
        self.autoMat.triScale = float(self.scaleLineEdit.text())

    def setTripBlend(self):
        self.autoMat.triBlend = float(self.blendLineEdit.text())
        print(self.autoMat.triBlend)

    def executeScript(self):
        """
        Start the pbr material setup method from autoMat
        """
        if self.triplanar:
            self.setTripScale()
            self.setTripBlend()
            self.setDispSubdiv()
            self.setDisplacementHeight()
            self.autoMat.setupMaterialTrip()
        else:
            self.setDispSubdiv()
            self.setDisplacementHeight()
            self.autoMat.setupMaterial(showInVP=self.showInVP)

    def resetMats(self):
        self.autoMat.cleanUp()

    def clearList(self):
        self.autoMat.dataDict.clear()
        self.populate()

    def dispVP(self, state):
        """
        Display materials in viewport or not

        Args:
            state (_type_): assigns checkbox status
        """
        self.showInVP = QtCore.Qt.Checked

    def switchTriPlanar(self, state):
        """
        Decidesif triplanar projection should be used or not based on set checkbox from UI.

        Args:
            state (_type_): assigns checkbox status
        """
        if state == QtCore.Qt.Checked:
            self.scaleLineEdit.setEnabled(True)
            self.blendLineEdit.setEnabled(True)
            self.triplanar = True
        else:
            self.triplanar = False
            self.scaleLineEdit.setEnabled(False)
            self.blendLineEdit.setEnabled(False)

    def switchCS(self):
        """
        switches colorspace based on UI values
        """
        if self.csDropdown.currentIndex() == 0:
            self.autoMat.csDefaults = ("sRGB", "Raw")
        elif self.csDropdown.currentIndex() == 1:
            self.autoMat.csDefaults = (
                "Input - Generic - sRGB - Texture", "Utility - Raw")

    def closeUI(self):
        cmds.deleteUI('AutoMat')


AutoMatUI(dock=True)
