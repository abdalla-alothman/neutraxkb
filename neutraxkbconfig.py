#!/usr/bin/env python3
import sys, re, os, subprocess
from glob import glob
from XkbConfig_ui import *
from PyQt4.QtGui import QApplication, QWidget, QMainWindow, QDialogButtonBox, QFileDialog, QSortFilterProxyModel, QStandardItemModel, QStandardItem, QIcon, QPixmap, QMessageBox, QStringListModel, QListWidgetItem
from PyQt4.QtCore import Qt, pyqtSlot, pyqtSignal, QModelIndex
from nxkbcfgparser import NXkbCfgParser

class NeutraXkbConfig(QMainWindow):
  reloadLayouts = pyqtSignal() 
  def __init__(self, parent=None):
    QMainWindow.__init__(self, parent)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    QApplication.setQuitOnLastWindowClosed(False)
    self.mod = False
    self.langList = []
    self.flagInfo = str()
    self.flagIcon = str()
    self.currentLayout = str()
    self.cfgInfo = NXkbCfgParser()
    # Lang Model
    self.model = QStringListModel(self.ui.langView)
    self.langFilter = QSortFilterProxyModel()
    # Flag Model
    self.fmodel = QStandardItemModel(self.ui.flagView)
    self.flagFilter = QSortFilterProxyModel()
    # Fill Views
    self.fillViews()
    # Init Lang Model
    self.model.setStringList(self.langList)
    self.langFilter.setSourceModel(self.model)
    self.ui.langView.setModel(self.langFilter)
    # Init Flag Model
    self.flagFilter.setSourceModel(self.fmodel)
    self.ui.flagView.setModel(self.flagFilter)
    # Set both filters to case insensitive
    self.langFilter.setFilterCaseSensitivity(Qt.CaseInsensitive)
    self.flagFilter.setFilterCaseSensitivity(Qt.CaseInsensitive)
    # Connections
    self.ui.lineEdit.textChanged[str].connect(self.langFilter.setFilterFixedString)
    self.ui.lineEdit_2.textChanged[str].connect(self.flagFilter.setFilterFixedString)
    self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.closeRequest)
    self.ui.flagView.clicked.connect(self.changeFlag)
    self.ui.langView.clicked.connect(self.updateIconDisplay)
    self.ui.addButton.clicked.connect(self.addLayout)
    self.ui.moveUpButton.clicked.connect(self.moveLangUp)
    self.ui.moveDownButton.clicked.connect(self.moveLangDown)
    self.ui.removeButton.clicked.connect(self.removeLang)
    self.ui.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(lambda: self.reloadRequested(self.mod))
    self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.okRequest)
    self.ui.browseButton.clicked.connect(self.addCustomIcon)
###############################################################################
  @pyqtSlot()
  def addLayout(self):
    if self.currentLayout == "":
      self.statusBar().showMessage("No layout selected.", 6000)
      return
    if self.flagInfo is "":
      self.flagIcon = self.cfgInfo.defaultIconDir() + "zz.png"
      self.flagInfo = "zz"
    listInfo = next(key for key, val in self.dataDict.items() if val == self.currentLayout) + " [{}]".format(self.currentLayout)
    if self.ui.resView.findItems(listInfo, Qt.MatchExactly): # Do not add if item is already in resView.
      return
    self.ui.resView.insertItem(self.ui.resView.count(), QListWidgetItem(QIcon(self.flagIcon), listInfo + " |{}|".format(self.flagInfo)))
    self.mod = True
######################################################################
  def okRequest(self):
    if self.mod:
      self.reloadRequested(True)
      self.closeRequest()
    else:
      self.closeRequest()
###############################################################################
  @pyqtSlot(QModelIndex)
  def updateIconDisplay(self, item1):
    self.currentLayout = self.dataDict[item1.data()].lower()
    if "/" in self.currentLayout:
      self.currentLayout = self.currentLayout.split("/")[1]
    self.ui.customFlagLabel.setText("Set Custom Icon for {}".format(item1.data()))
    self.flagIcon = os.path.abspath(self.cfgInfo.defaultIconDir() + self.currentLayout + ".png")
    if not os.path.exists(self.flagIcon):
      self.flagIcon = self.cfgInfo.defaultIconDir() + "zz.png"
    if os.path.isfile(self.flagIcon):
      self.ui.flagLabel.setPixmap(QPixmap(self.flagIcon))
      self.flagInfo = self.flagIcon.split("/")[-1].split(".")[0]
      self.statusBar().showMessage("{}".format(self.dataDict[item1.data()]), 6000)
      return
###############################################################################
  @pyqtSlot(QModelIndex)
  def changeFlag(self, flag):
    self.flagInfo = flag.data()
    self.flagIcon = os.path.abspath(self.cfgInfo.defaultIconDir() + flag.data().lower() + ".png")
    self.ui.flagLabel.setPixmap(QPixmap(self.flagIcon))
    self.flagInfo = flag.data().lower()
###############################################################################
  def fillViews(self):
    flagList = glob(os.path.abspath(self.cfgInfo.defaultIconDir() + "*.png"))
    flagList.sort()
    XkbLayouts = self.getXkbLayouts()
    for x in XkbLayouts: # fill layout listView
      for k in x.keys():
        self.langList.append(k)
    self.dataDict = {}
    for dict in XkbLayouts: # fill internal data dict
      for dName, isocode in dict.items():
        dispName = dName
        self.dataDict.update({dispName: isocode})
    self.langList.sort()
    for f in flagList: # fill the flag listView
      i = QStandardItem(f.split("/")[-1].split(".")[0].upper())
      i.setIcon(QIcon(f))
      self.fmodel.appendRow(i)
    self.ui.flagLabel.setPixmap(QPixmap(flagList[0]))
    self.fillResView()
    del flagList
    del XkbLayouts
###############################################################################
  def fillResView(self):
    self.ui.resView.clear()
    for langDict in self.cfgInfo.languages(): # fill added/available languages/layouts listwidget
      entryIcon1 = langDict["icon"]
      entryName = langDict["name"]
      entryLayout = langDict["layout"]
      i = QListWidgetItem(QIcon(entryIcon1), "{} [{}] |{}|".format(entryName, entryLayout, entryIcon1.split("/")[-1].split(".")[0]))
      self.ui.resView.addItem(i)
###############################################################################
  def getXkbLayouts(self):
    x = []
    try:
      with open("/usr/share/X11/xkb/rules/base.lst") as layouts:
        r = False
        for line in layouts:
          if line == "\n": continue
          if line.startswith("! layout"): r = True
          if re.search(r"^! [^ layout]", line) is not None: r = False
          if r == True:
            l = re.split(r"^\s|\s{2,15}", line.strip())
            if l[0] == "! layout":
              continue
            l.sort()
            x.append({l[0]: l[1]})
    except IOError as e:
      print("File not found.")
    return x
###############################################################################
  def addCustomIcon(self):
    m_dir = os.path.expanduser("~/")
    customIcon = QFileDialog.getOpenFileName(self, "Select Custom Icon", m_dir, "Image Files (*.png *.jpg *.gif)")
    if customIcon is "":
      return
    else:
      icon1 = QPixmap(customIcon)
      if icon1.width() > 128 or icon1.height() > 128:
        QMessageBox.warning(self, "Large Icon File", "The custom icon is too large.\nPlease select an Icon around the size of 24x24 pixels.")
        return
      else:
        self.flagInfo = customIcon
        self.ui.flagLabel.setPixmap(icon1)
        self.flagIcon = icon1
###############################################################################
  def moveLangUp(self):
    currentSelection = self.ui.resView.currentRow()
    currentLang = self.ui.resView.takeItem(currentSelection)
    self.ui.resView.insertItem(currentSelection - 1, currentLang)
    self.ui.resView.setCurrentItem(currentLang)
    layoutName = re.split(r" \[(.{2,8})\] ", currentLang.text())[1]
    self.cfgInfo.upgradeLang(layoutName)
    sectName = currentLang.text().split(" ")[0]
    sectName = sectName + "_" + layoutName
    self.cfgInfo.upgradeSection(sectName.lower())
    self.mod = True
###############################################################################
  def removeLang(self):
    lang = self.ui.resView.item(self.ui.resView.currentRow()).text()
    entry = re.split(r"([A-Za-z]{2,50})\s\(?.*\[(.{2,8})\]\s.*", lang)
    entry = list(filter(("").__ne__, entry))
    entry = "_".join(entry).lower()
    self.cfgInfo.removeLanguage(entry)
    self.ui.resView.takeItem(self.ui.resView.currentRow())
    self.mod = True
###############################################################################
  def moveLangDown(self):
    currentSelection = self.ui.resView.currentRow()
    currentLang = self.ui.resView.takeItem(currentSelection)
    self.ui.resView.insertItem(currentSelection + 1, currentLang)
    self.ui.resView.setCurrentItem(currentLang)
    layoutName = re.split(r" \[(.{2,8})\] ", currentLang.text())[1]
    self.cfgInfo.downgradeLang(layoutName)
    sectName = currentLang.text().split(" ")[0]
    sectName = sectName + "_" + layoutName
    self.cfgInfo.downgradeSection(sectName.lower())
    self.mod = True
###############################################################################
  def reloadRequested(self, sendSig=bool()):
    if sendSig == False: return
    for x in self.ui.resView.findItems("*", Qt.MatchWildcard):
      langInfo = x.text()
      langInfo = re.split(r"\s\[(.{2,8})\]", langInfo)
      cfgLabel = re.sub("([A-Za-z]{3,60})\s.*", r"\1", langInfo[0])
      cfgLabel = cfgLabel + "_{}".format(langInfo[1])
      self.flagInfo = langInfo[2].replace(" ", "").replace("|", "")
      if not self.flagInfo.startswith("/"):
        self.flagInfo = self.cfgInfo.defaultIconDir() + self.flagInfo + ".png"
      dTup = (cfgLabel, '{{"name": "{}", \n"label": "{}", \n"layout": "{}", \n"icon": "{}"}}\n'.format(langInfo[0], cfgLabel.split("_")[0], langInfo[1], self.flagInfo))
      self.cfgInfo.addLanguage(dTup)
      appendLayout = self.cfgInfo.get("deflayout", "currentLayout")
      if not langInfo[1] in appendLayout:
        appendLayout = appendLayout + ",{}".format(langInfo[1])
        self.cfgInfo.set("deflayout", "currentLayout", appendLayout)
      subprocess.call(["setxkbmap -layout {}".format(appendLayout)], shell=True)
      self.cfgInfo.writeCFG()
      self.cfgInfo.__init__()
      self.statusBar().showMessage("Added {}. Current layout: {}".format(langInfo[0], appendLayout), 6000)
      self.reloadLayouts.emit()
      self.mod = False
###############################################################################
  def closeRequest(self):
    self.ui.resView.clear()
    self.close()
    self.fillResView()
###############################################################################
if __name__ == "__main__":
  config1 = QApplication(sys.argv)
  xkbconfig = NeutraXkbConfig()
  xkbconfig.show()
  sys.exit(config1.exec_())

