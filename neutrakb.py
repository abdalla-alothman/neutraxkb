#!/usr/bin/env python3

import sys, subprocess, re, os, platform
from PyQt4.QtGui import QApplication, QSystemTrayIcon, QMenu, QIcon, QMessageBox
from PyQt4.QtCore import pyqtSlot, QT_VERSION_STR, PYQT_VERSION_STR
from neutraxkbconfig import NeutraXkbConfig
from nxkbcfgparser import NXkbCfgParser
class NeutraXkbSwitch(QSystemTrayIcon):
  def __init__(self, country=str(), parent=None):
    self.progName = "NeutraXkbSwitch"
    self.version = "1.0"
    QSystemTrayIcon.__init__(self, parent)
    self.cfgParser = NXkbCfgParser()
    self.nxkbConfig = NeutraXkbConfig()
    self.kbMap = dict()
    self.currentOpt = str()
    self.ckblayout = self.cfgParser.defaultLayouts()
    self.kbList = []
    self.updateKBList()
    self.loadSwitcher()
    self.show()
    self.activated[self.ActivationReason].connect(self.switchLang)
    self.nxkbConfig.reloadLayouts.connect(self.applyChanges)
###############################################################################
  def applyChanges(self):
    self.ckblayout = self.cfgParser.currentKBLayout()
    self.updateKBList()
    self.loadSwitcher()
################################################################################
  def updateKBList(self): 
    langDictList = self.cfgParser.languages()
    for ent in self.cfgParser.languages():
      self.kbMap.update({"{}".format(ent["layout"]): "{}".format(ent["icon"])})
    if re.match("([a-z]{1,5},{1,}?)", self.ckblayout):
      self.kbList = self.ckblayout.split(",")
      self.currentOpt = self.kbList[0]
      return
    else:
      self.kbList.append(self.ckblayout)
      self.currentOpt = self.ckblayout
      return
###############################################################################
  def langChangeRequest(self, lang):
    if lang in self.kbList:
      self.kbList.pop(self.kbList.index(lang))
      self.currentOpt = lang
      self.kbList.insert(0, lang)
      self.setIcon(QIcon(self.kbMap[self.currentOpt]))
      subprocess.call(["setxkbmap -layout {}".format(",".join(self.kbList))], shell=True)
###############################################################################
  @pyqtSlot(QSystemTrayIcon.ActivationReason)
  def switchLang(self, click):
    self.currentLayout = self.cfgParser.get("deflayout", "currentLayout")
    self.kbList = self.currentLayout.split(",")
    if click in(QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick, self.MiddleClick):
      icon1 = self.kbList[(self.kbList.index(self.currentOpt) + 1) % len(self.kbList)]
      self.currentOpt = icon1
      self.kbList.pop(self.kbList.index(self.currentOpt))
      self.kbList.insert(0, self.currentOpt)
      self.setIcon(QIcon(self.kbMap[self.currentOpt]))
      subprocess.call(["setxkbmap -layout {}".format(",".join(self.kbList))], shell=True)
      return
###############################################################################
  def loadSwitcher(self):
    lmenu = QMenu()
    lmenu.clear()
    def loadAct(l):
      lmenu.addAction(l, lambda: self.langChangeRequest(l))
    for x in self.kbList:
      loadAct(x)
    lmenu.addSeparator()
    lmenu.addAction("Configure", lambda: self.nxkbConfig.show())
    lmenu.addAction("About", self.showAbout)
    lmenu.addAction("Quit", lambda: sys.exit(0))
    self.setContextMenu(lmenu)
    self.setIcon(QIcon(self.kbMap[self.currentOpt]))
###############################################################################
  def showAbout(self):
    QMessageBox.about(self.nxkbConfig, "About NeutraXkbSwich",
        """<h2>{} {}</h2>
        <p>A Python/PyQt4 tool to globally switch between X keyboard layouts.</p>
        <p>Copyright &copy; 2014 - Abdalla Saeed Abdalla Alothman<br />
        Kuwait - July 17, 2014<br />
        <a href="mailto:abdallah.alothman@gmail.com">abdallah.alothman@gmail.com</a>
        </p>
        <h3>Credits</h3>
        <p>Application Icon: <a href="http://www.pinterest.com/pin/188517934376093096/">Say Cheese (Finger Art, at Tumblr)</a>
        <br />
        Flag Icons: <a href="http://kampongboy92.deviantart.com/art/World-Flags-63208143">World Flags, by kampongboy92</a>
        </p>
        <p><b>{}</b> is currently using Python {} with Qt {} and PyQt {} on your system ({}).</p>""".format(self.progName,
          self.version, self.progName, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))
###############################################################################
if __name__ == "__main__":
  sys.settrace
  import signal
  signal.signal(signal.SIGINT, signal.SIG_DFL)
  kbswitcher = QApplication(sys.argv)
  if not QSystemTrayIcon.isSystemTrayAvailable():
    from PyQt4.QtGui import QMessageBox
    QMessageBox.critical(None, "XKBSwitcher",
        "No current system tray is served on this desktop.\nTry running a panel with a system tray \(e.g. razor-panel or tint2.\)")
    sys.exit(1)
  xbswitcher = NeutraXkbSwitch()
  sys.exit(kbswitcher.exec_())
