import configparser, ast, sys, os, subprocess, re
class NXkbCfgParser(configparser.ConfigParser):
  def __init__(self):
    configparser.ConfigParser.__init__(self)
    self.cfg = os.path.expanduser("~/.config/neutraxkb/neutraxkb.conf")
    if not os.path.exists(os.path.expanduser(self.cfg)):
      self.firstRun()
      self.read(self.cfg)
      self.iconDir = self.get("deficons", "iconDir")
      self.langs = self.items("languages")
      self.exportDefault()
    else:
      self.read(self.cfg)
      self.iconDir = self.get("deficons", "iconDir")
      self.langs = self.items("languages")
###############################################################################
  def firstRun(self):
    if os.path.isdir(os.path.expanduser("~/.config/neutraxkb")) and not os.path.isfile(self.cfg):
      open(self.cfg, "w+").close()
      self.addDefs()
    elif os.path.isfile(os.path.expanduser(self.cfg)) is not None:
      if not os.path.exists(os.path.expanduser("~/.config/nutraxkb")):
        os.makedirs(os.path.expanduser("~/.config/neutraxkb"))
        self.addDefs()
    self.writeCFG()
###############################################################################
  def addDefs(self):
    self.add_section("deficons")
    self.set("deficons", "iconDir", "/usr/share/neutraxkb/world-flags/")
    self.add_section("customIcons")
    self.add_section("deflayout")
    kblayout = self.currentKBLayout()
    self.set("deflayout", "currentLayout", kblayout)
    self.add_section("languages")
    self.writeCFG()
###############################################################################
  def languages(self):
    self.read(self.cfg)
    self.langs = self.items("languages")
    mainList = []
    for x in self.langs:
      # convert tuple to dict
      c = ast.literal_eval(self.get("languages", x[0]))
      # append dict to list
      mainList.append(c)
    return mainList
###############################################################################
  def addLanguage(self, langTuple):
    self.set("languages", langTuple[0], langTuple[1])
###############################################################################
  def removeLanguage(self, locale):
    self.remove_option("languages", locale)
    self.removeSystemLayout(locale.split("_")[1])
    self.writeCFG()
###############################################################################
  def writeCFG(self):
    with open(self.cfg, "w") as cfgfile:
      self.write(cfgfile)
###############################################################################
  def currentKBLayout(self):
    kb_layout = subprocess.check_output("setxkbmap -query |grep layout | cut -d':' -f2|xargs", shell=True)
    kb_layout = bytes.decode(kb_layout).strip()
    #kb_layout = self.get("deflayout", "currentLayout")
    return kb_layout
###############################################################################
  def defaultLayouts(self):
    return self.get("deflayout", "currentLayout")
##############################################################################
  def defaultIconDir(self):
    return self.iconDir
###############################################################################
  def removeSystemLayout(self, layout):
    layoutList = self.get("deflayout", "currentLayout").split(",")
    if not layout in layoutList:
      print("Not in layoutlist")
      subprocess.call(["setxkbmap -layout {}".format(self.get("deflayout", "currentLayout"))], shell=True)
      return
    layoutList.pop(layoutList.index(layout))
    newLayout = ",".join(layoutList)
    self.set("deflayout", "currentLayout", newLayout)
    subprocess.call(["setxkbmap -layout {}".format(newLayout)], shell=True)
###############################################################################
  def downgradeLang(self, layoutName):
    layoutList = self.get("deflayout", "currentLayout").split(",")
    if layoutName not in layoutList:
      return
    currentIndex = layoutList.index(layoutName)
    layoutList.pop(currentIndex)
    layoutList.insert(currentIndex + 1, layoutName)
    self.set("deflayout", "currentLayout", ",".join(layoutList))
###############################################################################
  def downgradeSection(self, sectName):
    langSectList = self.items("languages")
    index = 0
    for langSect in range(len(langSectList)):
      if sectName in langSectList[langSect][0]:
        tup = langSectList[langSect]
        index = langSect
    tup = langSectList.pop(index)
    langSectList.insert(index + 1, tup)
    self.remove_section("languages")
    self.add_section("languages")
    for langSect in langSectList:
      self.addLanguage(langSect)
###############################################################################
  def upgradeLang(self, layoutName):
    layoutList = self.get("deflayout", "currentLayout").split(",")
    if layoutName not in layoutList:
      return
    currentIndex = layoutList.index(layoutName)
    layoutList.pop(currentIndex)
    layoutList.insert(currentIndex - 1, layoutName)
    self.set("deflayout", "currentLayout", ",".join(layoutList))
###############################################################################
  def upgradeSection(self, sectName):
    langSectList = self.items("languages")
    index = 0
    for langSect in range(len(langSectList)):
      if sectName in langSectList[langSect][0]:
        tup = langSectList[langSect]
        index = langSect
    tup = langSectList.pop(index)
    langSectList.insert(index - 1, tup)
    self.remove_section("languages")
    self.add_section("languages")
    for langSect in langSectList:
      self.addLanguage(langSect)
###############################################################################
  def exportDefault(self):
    currentLayout = self.currentKBLayout().split(",")
    xkblist = []
    newLangEntry = str()
    import glob
    flagDir = glob.glob(self.iconDir + "*.png")
    try:
      with open("/usr/share/X11/xkb/rules/base.lst") as layouts:
        r = False
        for line in layouts:
          if line == "\n": continue
          if line.startswith("! layout"): r = True
          if re.search(r"^! [^ layout]", line) is not None: r = False
          if r == True:
            l = re.split(r"^\s|\s{2,15}", line.strip())
            if l[0] == "! layout": continue
            xkblist.append({l[0]: l[1]})
    except IOError:
      print("base.lst: File not found.")
    for x in currentLayout:
      for dict in xkblist:
        if x in dict.keys(): 
          idName = re.split(r"\s(\(.*)", dict[x])[0].strip()
          label = idName
          xname = dict[x]
          lout = x
          idName = idName + "_" + x
          check = self.iconDir + x + ".png"
          if check in flagDir:
            icon = check
          else:
            icon = self.iconDir + "zz.png"
          self.addLanguage(("{}".format(idName), '{{"name": "{}", \n"label": "{}", \n"layout": "{}", \n"icon": "{}"}}\n'.format(xname, label, lout, icon)))
      self.writeCFG()
###############################################################################
