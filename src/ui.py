from main import autoMat
from importlib import reload
from PySide2 import QtWidgets, QtCore, QtGui  # TODO change to Qt later
import main
reload(main)  # TODO remove later only for WIP with maya


class AutoMatUI(QtWidgets.QDialog):

    def __init__(self):
        super(AutoMatUI, self).__init__()
        """
        This class holds all necessary variables and methods to build, populate and update the UI. 
        """
        self.setWindowTitle('AutoMat')

        # TODO setup window size relativ to screen size
        self.autoMat = autoMat()
        self.buildUI()
        self.populate()
        self.triplanar = False
        self.showInVP = True

    def buildUI(self):
        """
        Creates all GUI elemnts and links each signla to their respective Method
        """
        layout = QtWidgets.QVBoxLayout(self)

        loadWidget = QtWidgets.QWidget()
        loadLayout = QtWidgets.QHBoxLayout(loadWidget)
        layout.addWidget(loadWidget)

        self.loadNameField = QtWidgets.QLineEdit()
        self.loadNameField.insert('No texture folder selected')
        self.loadNameField.setStyleSheet("font-size: 11pt")
        self.loadNameField.textChanged.connect(self.updatePath)
        loadLayout.addWidget(self.loadNameField)

        loadBtn = QtWidgets.QPushButton('select')
        loadBtn.setStyleSheet("font-size: 11pt")
        loadBtn.clicked.connect(self.chooseDirectory)
        loadLayout.addWidget(loadBtn)

        self.listWidget = QtWidgets.QListWidget()
        layout.addWidget(self.listWidget)

        statusWidget = QtWidgets.QWidget()
        statusLayout = QtWidgets.QHBoxLayout(statusWidget)
        layout.addWidget(statusWidget)

        self.statusLabel = QtWidgets.QLabel()
        statusLayout.addWidget(self.statusLabel)

        optionWidget = QtWidgets.QWidget()
        optionLayout = QtWidgets.QHBoxLayout(optionWidget)
        layout.addWidget(optionWidget)

        vpCompCheck = QtWidgets.QCheckBox("Display in Viewport")
        vpCompCheck.setChecked(True)
        vpCompCheck.setStyleSheet("font-size: 12pt")
        vpCompCheck.stateChanged.connect(self.dispVP)
        optionLayout.addWidget(vpCompCheck)

        triPlanarCheck = QtWidgets.QCheckBox(
            "Triplanar (broken in viewport)")
        triPlanarCheck.setStyleSheet("font-size: 12pt")
        triPlanarCheck.stateChanged.connect(self.switchTriPlanar)
        optionLayout.addWidget(triPlanarCheck)

        self.csDropdown = QtWidgets.QComboBox()
        self. csDropdown.addItem("Maya ACES")
        self.csDropdown.addItem("General ACES")
        self.csDropdown.setStyleSheet("font-size: 11pt")
        self.csDropdown.currentIndexChanged.connect(self.switchCS)
        optionLayout.addWidget(self.csDropdown)

        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout(btnWidget)
        layout.addWidget(btnWidget)

        importBtn = QtWidgets.QPushButton('Setup Materials')
        importBtn.setStyleSheet("font-size: 11pt")
        importBtn.clicked.connect(self.executeScript)
        btnLayout.addWidget(importBtn)

        resetBtn = QtWidgets.QPushButton('Reset Files')
        resetBtn.setStyleSheet("font-size: 11pt")
        resetBtn.clicked.connect(self.clearList)
        btnLayout.addWidget(resetBtn)

        closeBtn = QtWidgets.QPushButton('Close')
        closeBtn.setStyleSheet("font-size: 11pt")
        closeBtn.clicked.connect(self.close)
        btnLayout.addWidget(closeBtn)

    def populate(self):
        """
        This Methods assigns all given data to the UI elements
        """
        self.loadNameField.setText(self.autoMat.dataPath)

        self.listWidget.clear()
        for keys, values in self.autoMat.dataDict.items():
            self.listWidget.addItem(keys)
            self.listWidget.addItems(values)

        self.listWidget.setStyleSheet("font-size: 11pt")

        folderCount = len(self.autoMat.dataDict.keys())
        if folderCount == 1:
            self.statusLabel.setText(
                f"Found {folderCount} texture folder.")
        else:
            self.statusLabel.setText(
                f"Found {folderCount} texture folders.")

        self.statusLabel.setStyleSheet("font-size: 13pt")

    def chooseDirectory(self):
        """
        This Opens a fie dialog and assigns the selected directory to the path to the autoMats instance dataPath variable
        """
        dialog = QtWidgets.QFileDialog(self)
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

    def executeScript(self):
        """
        Start the pbr material setup method from autoMat
        """
        if self.triplanar:
            self.autoMat.setupMaterialTrip()
        else:
            self.autoMat.setupMaterial(showInVP=self.showInVP)

    def clearList(self):
        self.autoMat.dataDict.clear()
        self.populate()

    def dispVP(self, state):
        """
        Display materials in viewport or not

        Args:
            state (_type_): assigns checkbox status
        """
        if state == QtCore.Qt.Checked:
            self.showInVP = True
        else:
            self.showInVP = False

    def switchTriPlanar(self, state):
        """
        Decidesif triplanar projection should be used or not based on set checkbox from UI.

        Args:
            state (_type_): assigns checkbox status
        """
        if state == QtCore.Qt.Checked:
            self.triplanar = True
        else:
            self.triplanar = False

    def switchCS(self):
        """
        switches colorspace based on UI values
        """
        if self.csDropdown.currentIndex() == 0:
            self.autoMat.csDefaults = ("sRGB", "Raw")
        elif self.csDropdown.currentIndex() == 1:
            self.autoMat.csDefaults = (
                "Input - Generic - sRGB - Texture", "Utility - Raw")


def showUI():
    ui = AutoMatUI()
    ui.show()
    return ui


ui = showUI()
