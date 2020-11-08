import os
import gettext

gettext.bindtextdomain('FeudalWorld', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'i18n'))
gettext.textdomain('FeodalWorld')
_ = gettext.gettext

str_resources=[_("File name")
, _("Enter the name of file/map"), _("Name is required"), _("{} is opened ({} edition)"), _("Regen"), _("Open"), _("Save"), _("Save as"), _("Exit"), _("File"), _("Visual")
, _("Values"), _("Pincette"), _("Marking"), _("Frame"), _("Select"), _("Pen"), _("Fill"), _("Insert"), _("Tools"), _("Load metadata...")
, _("Loading a map"), _("Please wait. Loading in progress..."), _("Mapping data to controllers options..."), _("Init controlls..."), _("Map metadata"), _("Domains"), _("Hierarchy"), _("Marks"), _("Windows"), _("Map: {}")
, _("{}x{}"), _("Modify"), _("Pinc"), _("Mark"), _("Rect"), _("Composising a controllers..."), _("Draw a current map's layer..."), _("Map generation"), _("Map in saving"), _("Rasterization of layers...")
, _("Save a map in file..."), _("Done"), _("Enter a name of new file/map. Map will rewrite if you close this window."), _("Map is modified. If you will close now, you lost all changes. Are you want save and rewrite map?"), _("Warning! Unsaved modifies."), _("File {} is not found (latest {})"), _("Main options of Map"), _("{} properties"), _("Name:"), _("Size:")
, _("Player's not more than:"), _("Age by default:"), _("Heights diapazone:"), _("Top and Bottom cells count:"), _("Map generator (pattern):"), _("OK"), _("Cancel"), _("Neolit"), _("Bronze"), _("Iron")
, _("Midieval"), _("Industrial"),
]
