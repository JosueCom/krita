'''
This script is licensed CC 0 1.0, so that you can learn from it.

------ CC 0 1.0 ---------------

The person who associated a work with this deed has dedicated the work to the public domain by waiving all of his or her rights to the work worldwide under copyright law, including all related and neighboring rights, to the extent allowed by law.

You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.

https://creativecommons.org/publicdomain/zero/1.0/legalcode
'''
from . import documenttoolsdialog
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFormLayout, QListWidget, QAbstractItemView,
                             QDialogButtonBox, QVBoxLayout, QFrame, QTabWidget,
                             QPushButton, QAbstractScrollArea, QMessageBox)
import krita
import importlib


class UIDocumentTools(object):

    def __init__(self):
        self.mainDialog = documenttoolsdialog.DocumentToolsDialog()
        self.mainLayout = QVBoxLayout(self.mainDialog)
        self.formLayout = QFormLayout()
        self.documentLayout = QVBoxLayout()
        self.refreshButton = QPushButton("Refresh")
        self.widgetDocuments = QListWidget()
        self.tabTools = QTabWidget()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.kritaInstance = krita.Krita.instance()
        self.documentsList = []

        self.refreshButton.clicked.connect(self.refreshButtonClicked)
        self.buttonBox.accepted.connect(self.confirmButton)
        self.buttonBox.rejected.connect(self.mainDialog.close)

        self.mainDialog.setWindowModality(Qt.NonModal)
        self.widgetDocuments.setSelectionMode(QAbstractItemView.MultiSelection)
        self.widgetDocuments.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def initialize(self):
        self.loadDocuments()
        self.loadTools()

        self.documentLayout.addWidget(self.widgetDocuments)
        self.documentLayout.addWidget(self.refreshButton)

        self.formLayout.addRow('Documents', self.documentLayout)
        self.formLayout.addRow(self.tabTools)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.line)
        self.mainLayout.addWidget(self.buttonBox)

        self.mainDialog.resize(500, 300)
        self.mainDialog.setWindowTitle("Document Tools")
        self.mainDialog.setSizeGripEnabled(True)
        self.mainDialog.show()
        self.mainDialog.activateWindow()

    def loadTools(self):
        modulePath = 'documenttools.tools'
        toolsModule = importlib.import_module(modulePath)
        modules = []

        for classPath in toolsModule.ToolClasses:
            _module = classPath[:classPath.rfind(".")]
            _klass = classPath[classPath.rfind(".") + 1:]
            modules.append(dict(module='{0}.{1}'.format(modulePath, _module),
                                klass=_klass))

        for module in modules:
            m = importlib.import_module(module['module'])
            toolClass = getattr(m, module['klass'])
            obj = toolClass(self.mainDialog)
            self.tabTools.addTab(obj, obj.objectName())

    def loadDocuments(self):
        self.widgetDocuments.clear()

        self.documentsList = [document for document in self.kritaInstance.documents() if document.fileName()]

        for document in self.documentsList:
            self.widgetDocuments.addItem(document.fileName())

    def refreshButtonClicked(self):
        self.loadDocuments()

    def confirmButton(self):
        selectedPaths = [item.text() for item in self.widgetDocuments.selectedItems()]
        selectedDocuments = [document for document in self.documentsList for path in selectedPaths if path == document.fileName()]

        self.msgBox = QMessageBox(self.mainDialog)
        if selectedDocuments:
            widget = self.tabTools.currentWidget()
            widget.adjust(selectedDocuments)
            self.msgBox.setText("The selected documents has been modified.")
        else:
            self.msgBox.setText("Select at least one document.")
        self.msgBox.exec_()
