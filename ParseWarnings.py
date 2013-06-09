import sublime, sublime_plugin
import collections, re, os

WarningKey = ": warning :"
MessageReg =  re.compile(".*pragma-messages]")
FileNameReg = re.compile("(^.*)\(.*\):")
OwnerReg = re.compile("^.*[oO]?wner[:]?[ \t]+([a-zA-Z ]*)", re.IGNORECASE)
DefaultOwner = "default"
BasePath = "e:/Projects/Institute"

SearchPaths = [ "BSAnimation", "BSAudio", "BSCore", "BSDevices", "BSDiag",
  "BSGraphics", "BSHavok", "BSMain", "BSMenu", "BSMovie", "BSPathfinding",
  "BSResource", "BSScript", "BSShader", "BSSystem", "BSSystemMonitor",
  "BSSystemUtilities", "FaceGen", "Gamebryo/CoreLibs/NiAnimation", "Gamebryo/CoreLibs/NiCollision",
  "Gamebryo/CoreLibs/NiMain", "Gamebryo/CoreLibs/NiParticle", "Gamebryo/CoreLibs/NiSystem",
  "Game/AI", "Game/AI/Animation", "Game/AI/Camera", "Game/AI/Combat",
  "Game/AI/CustomPackages", "Game/AI/Detection", "Game/AI/Movement",
  "Game/Audio", "Game/Debug", "Game/Dialogue", "Game/Interface", "Game/Magic",
  "Game/Misc", "Game/SaveGame", "Game/Script", "Shared/AI", "Shared/Animation", "Shared/Audio",
  "Shared/Camera", "Shared/Clouds", "Shared/DistantTerrain", "Shared/Events", "Shared/ExtraData",
  "Shared/FaceGen", "Shared/FileIO", "Shared/FormComponents", "Shared/Formulas", "Shared/Havok",
  "Shared/LOS", "Shared/Magic", "Shared/Misc", "Shared/Pathfinding", "Shared/Radiant Story",
  "Shared/Regions", "Shared/Sky", "Shared/SpeedTree", "Shared/TempEffects", "Shared/TESForms",
  "Shared/Water", "Shared/TESForms/Character", "Shared/TESForms/Gameplay", "Shared/TESForms/Objects",
  "Shared/TESForms/World" ]

def FindFile( aPath, aFileName ) :
  myFile = None
  try:
    myFile = open(aFileName)
  except:
    pass

  if myFile == None :
    # print "Didn't find file " + aFileName + "\r\n"
    aFileName = os.path.basename(aFileName)
    # print "Walking " + aPath + " looking for " + aFileName
    for sd in SearchPaths :
      spath = os.path.join(aPath, sd)
      # print "looking in " + spath
      names = os.listdir(spath)
      if aFileName in names:
        fname = os.path.join(spath, aFileName)

        # print "Found file in " + fname + "\r\n"
        myFile = open(fname)
        break

  return myFile

def FindName( aLine ) :
  res = FileNameReg.match(aLine)
  if (res != None) :
    # Open file.
    # print "opening file " + res.group(1)
    f = FindFile(BasePath, res.group(1))
    if (f != None) :
      for i in range(0, 40) :
        ln = f.readline(4096)
        # print "looking for owner on " + ln
        owner = OwnerReg.match(ln)
        if (owner != None) :
          # print "found owner " + owner.group(1)
          name = owner.group(1)
          f.close()
          return name.strip()
      f.close()

  return None

def IsNotMessage( aLine ) :
  return(MessageReg.match(aLine) == None);

class ParseWarningsCommand( sublime_plugin.TextCommand ) :
  def reset( self ) :
    self.Owners = {  } #Dictionary of owner/File list pairs.

  def WriteToOutput( self, edit, data ) :
    vw = self.view

    w = vw.window()
    fpath, fext = os.path.splitext(vw.file_name())
    fname = os.path.basename(fpath)
    outputVW = w.new_file()
    outputVW.set_name(fname + "Warnings")
    outputVW.set_scratch(True)
    offset = 0
    numWarnings = 0

    for o in data :
      hdr = "\r\nWarnings for " + o[0] + '(' + str(len(o[1])) + '):\r\n'
      offset += outputVW.insert(edit, offset, hdr)

      numWarnings += len(o[1])
      for m in o[1] :
        entry = "   " + m + '\r\n'
        offset += outputVW.insert(edit, offset, entry)

    msg = "---Found " + str(numWarnings) + " warnings in " + fname + "---\r\n"
    outputVW.insert(edit, 0, msg)

  def run( self, edit ) :
    self.reset()

    vw = self.view

    warningRegs = vw.find_all(WarningKey)

    for r in warningRegs :
      ln = vw.line(r)
      txt = vw.substr(ln)
#      print "looking at " + txt
      if (IsNotMessage(txt)) :
        # open file and find owner.
        name = FindName(txt)

        # If no owner add to the default person.
        if name == None :
          name = DefaultOwner
          txt = txt

        msgs = self.Owners.get(name)
        # if person not in dictionary add.
        if (msgs == None) :
          msgs = [txt]
          self.Owners[name] = msgs
        else: # else add to owner.
          msgs.append(txt)

    # email owners
    owners = self.Owners.items()
    self.WriteToOutput(edit, owners)

SourceFileReg = re.compile(".*\.(cpp|h|inl)$")

def NoOwner( aFile ) :
  with open(aFile) as f :
    for i in range(0, 40) :
      ln = f.readline(4096)
      # print "looking for owner on " + ln
      owner = OwnerReg.match(ln)
      if (owner != None) :
        # print "found owner " + owner.group(1)
        return False
  return True

class VerifyOwnerCommand( sublime_plugin.TextCommand ) :

  def run( self, edit ) :
    vw = self.view
    w = vw.window()
    outputVW = w.new_file()
    outputVW.set_name("OwnerIssues")
    outputVW.set_scratch(True)
    offset = 0;
    missingOwners = 0

    for dirname, dirnames, filenames in os.walk('e:\projects\Institute\BSCore'):
      # print path to all filenames.
      for filename in filenames:
        sourceFile = SourceFileReg.match(filename)
        if (sourceFile != None) :
          theFile = os.path.join(dirname, filename)
          if NoOwner(theFile) :
            missingOwners += 1
            msg = "\r\n" + theFile
            offset += outputVW.insert(edit, offset, msg)

    msg = "---Found " + str(missingOwners) + " files with no owner---\r\n"
    outputVW.insert(edit, 0, msg)
