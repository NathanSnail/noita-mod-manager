import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import os
import subprocess
import ast
import regex as re
import math

steam_path = "\\".join(["D:", "Steam"])

workshop_dir = steam_path + "\\" + "\\".join(
	["steamapps", "Workshop", "Content", "881100"]
)
mods_dir = steam_path + "\\" + "\\".join(
	["steamapps", "common", "Noita", "mods"]
)
_ = """
-------[Search]-------
-------[Filter: enabled/disabled/all]----
[Apply]
[Mod Name] (hover desc)
[Name]
[Name]
[Name]
[Name]
[Name]
------[Profiles]-------
save current list as profile: [Name]
load profile [Search]
[Name] [delete]
[Name] [delete]
"""


if input("dev (y/n): ").lower() == "y":
	mc = "\\".join(["D:", "Steam", "steamapps", "common", "noita", "save00", "mod_config.xml"])
else:
	mc = "\\".join(["C:", "Users", "natha", "AppData", "LocalLow", "Nolla_Games_Noita", "save00", "mod_config.xml"])
tree = ET.parse(mc)
root = tree.getroot()


def XML(file_name):
	file_safe = file_name.replace("\\", "\\\\")
	print(file_safe)
	command = ['lua', '-e',
			   f"\"require('remote');val=parse_xml('{file_safe}');print(val);\""]
	command = " ".join(command)
	content = subprocess.check_output(
		command
	)
	# print(content)
	temp = {}
	content = str(content)[2:-5]
	temp = ast.literal_eval(content)
	return temp


mods = []
for val in root.iter():
	if val.attrib == {}:
		continue
	mods.append(val.attrib)
	name = "Unknown"
	desc = "Unknown"
	# print(mods[-1]["name"])
	# print(mods[-1]["workshop_item_id"])
	if mods[-1]["workshop_item_id"] == "0":
		mt = XML(mods_dir+"\\"+mods[-1]["name"]+"\\mod.xml")
	else:
		mt = XML(workshop_dir+"\\" +
				 mods[-1]["workshop_item_id"]+"\\mod.xml")
	name = mt["name"]
	desc = mt["description"]
	mods[-1]["ui_name"] = name
	mods[-1]["ui_desc"] = desc


seen = []

mods_col = [
]
for mod in mods:
	mod_id = mod["name"]
	mod_name = mod["ui_name"]
	enabled = mod["enabled"] == "1"
	if mod_id in seen:
		raise Exception(
			f"Found duplicate mod-id {mod_id} called {mod_name}, remove the workshop or local copy of the mod to continue.")
	seen.append(mod_id)
	mods_col.append([sg.Checkbox(mod_name, enabled, key=mod_id,pad=(0,0))])

profiles = [("Vanilla", [])]
with open("profiles.txt", "r") as file:
	content = file.read()
	lines = content.split("\n")
	for i in range(len(lines)//2):
		profiles.append((lines[2*i], ast.literal_eval(lines[2*i+1])))
profile_button = sg.Button("Load", size=(8, 1))


profile_selector = sg.Combo(values=["Profile: " + x[0] for x in profiles],
							size=(2**15, 1), enable_events=True, key="profile_selector")


profile_box = sg.InputText(size=(2**15, 1))

search_box = sg.InputText(size=(2**15, 1))

def search():
	text = search_box.get().lower()
	for row in col.Rows:
		box = row[0]
		name = box.Text
		if not text in name.lower():
			box.hide_row()
			# box.set_size((0,0))
			box.update(visible=False)
		else:
			# print(dir(box))
			# print(box.element_frame)
			box.unhide_row()
			# box.set_size((None,None))
			# box.align
			box.update(visible=True)


def disable_all():
	pass

def profile_save():
	global profiles
	global profile_selector
	name = profile_box.get()
	idx = None
	mods_enabled = []
	for row in col.Rows:
		box = row[0]
		val = box.get()
		if val:
			mods_enabled.append(box.key)
	with open("profiles.txt","r") as file:
		content = file.read()
	for k,profile in enumerate(content.split("\n")):
		if profile == name:
			idx = k//2
	if idx is not None:
		print("save main")
		lines = content.split("\n")
		lines[2*idx+1] = str(mods_enabled)
		content = "\n".join(lines)
		profiles[idx+1] = (name,mods_enabled) # +1 because vanilla is special
		with open("profiles.txt","w") as file:
			file.write(content)
	else:
		print("save alt")
		lines = content.split("\n")
		lines.append(name)
		lines.append(str(mods_enabled))
		content = "\n".join(lines)
		profiles.append((name,mods_enabled))
		with open("profiles.txt","w") as file:
			file.write(content)
	profile_selector.update(values=["Profile: " + x[0] for x in profiles])
	print(profiles)

def apply():
	out = "<Mods>\n"
	for row in col.Rows:
		box = row[0]
		val = box.get()
		mod_id = box.key
		for value in mods:
			if value["name"] == mod_id:
				fold = value["settings_fold_open"]
				workshop_id = value["workshop_item_id"]
				out += f"<Mod enabled=\"{1 if val else 0}\" name=\"{mod_id}\" settings_fold_open=\"{1 if fold else 0}\" workshop_item_id = \"{workshop_id}\"> </Mod>\n"
	out += "</Mods>"
	with open(mc,"w") as file:
		file.write(out)


def profile_load():
	target = profile_selector.Get()[len("Profile: "):]
	for val in profiles:
		if val[0] == target:
			load(val[1])


def load(modlist):
	print("goon")
	print("\n".join(modlist))
	for row in col.Rows:
		box = row[0]
		box.update(box.key in modlist)


		# print(dir(box))
		# print(f"{box.Text}: {box.get()}")
col = sg.Column(mods_col, scrollable=True,
				vertical_scroll_only=True, size=(2**15, 2**15),element_justification="left",vertical_alignment="top",pad=(0,0))
layout = [
	[
		sg.Button("Apply", size=(8, 1)),
		sg.Button("Enable All", size=(8, 1)),
		sg.Button("Disable All", size=(8, 1)),
		sg.Listbox(["Filter Mode: " + x for x in ["All",
				   "Enabled", "Disabled"]], size=(2**15, 1)),
	],
	[
		sg.Button("Search", size=(8, 1)),
		search_box
	],
	[
		sg.Button("Save", size=(8, 1)),
		profile_box
	],
	[
		profile_button,
		profile_selector,
	],
	[
		col,
	]
]
window = sg.Window("Mod Manager", layout, icon='sampo.ico', size=(640, 360), resizable=True, finalize=True)
# profile_button.bind('<Button-1>',prof)
window.bind('<Configure>', "Event")
profile_button.bind('<Button-1>', "LoadProfile")
while True:
	event, values = window.read()
	# End program if user closes window or
	# presses the OK button
	if event == "OK" or event == sg	.WIN_CLOSED:
		break
	if event == "Event":
		size = window.size
		# col.set_size((size[0],2**15))
	if event == "Load":
		profile_load()
	if event == "Apply":
		apply()
	if event == "Save":
		profile_save()
	if event == "Search":
		print("searching")
		search()


window.close()
