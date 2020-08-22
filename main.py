

import curses, time, ast, traceback, random, os, threading

import cProfile, pstats, io

from pathlib import Path
from zipfile import ZipFile

# do not delete useless imports!

from kernel import *


DEV = "dev"
PRODUCTION = "production"

VERSION = DEV

CRASH_REPORT_FILENAME = "crash_report.txt"


def get_doc(file):

	tree = ast.parse(file.read())

	return ast.get_docstring(tree) or ""

def get_info(file):
	"""

	:param file:
	:return: (requirements, packname)
	"""

	doc = get_doc(file)
	req = []
	packname = None

	for line in doc.split("\n"):

		if line.startswith("REQ"):

			spl = line[3:].split(",")
			req += [r.strip() for r in spl]

		if line.startswith("PATCH"):

			packname = line.split(" ")[1]

	return tuple(req), packname

def load_pack(path: Path):

	if path.suffix != ".zip": path = path.parent / (path.name + ".zip")

	print(f" + Loading {path}")

	structure = []

	with ZipFile(path) as zfile:

		for zipinfo in zfile.infolist():

			filename = zipinfo.filename

			if Path(filename).suffix in (".component", ".game_object", ".space", ".state", ".state_manager"):

				req, packname = get_info(zfile.open(filename))

				if packname is None:
					packname = path.stem

				structure.append((Path(filename).name, req, zfile.open(filename), packname))
				# I have to open the file two times, due to the content of the file being 'consumed' on .read

			else:
				load_item(zfile.open(filename), Path(filename), path.stem)
				#print(f"\tIgnored {filename}")

	loaded = set()

	while structure:

		item = structure.pop(0)

		"""
		print("===============")
		print("REQ: ", item[1])
		print("LOD: ", loaded)
		"""

		if all([r in loaded for r in item[1]]):

			loaded.add(item[0])
			load_item(item[2], Path(item[0]), item[3])

		else:
			structure.append(item)

	print("Done")

def load_item(file, path: Path, packname):

	if packname not in Data.components:

		Data.components[packname] = {}
		Data.game_objects[packname] = {}
		Data.spaces[packname] = {}
		Data.states[packname] = {}
		Data.files[packname] = {}

	Data.exported = None
	content = None

	if path.suffix in (".component", ".game_object", ".space", ".state", ".state_manager"):
		exec(file.read().decode("utf-8"))

	else:
		content = file.read().decode("utf-8")

	if path.suffix == ".component":
		Data.exported.name = path.stem
		Data.exported.packname = packname
		Data.components[packname][path.stem] = Data.exported

	elif path.suffix == ".game_object":
		Data.game_objects[packname][path.stem] = Data.exported

	elif path.suffix == ".space":
		Data.spaces[packname][path.stem] = Data.exported

	elif path.suffix == ".state":
		Data.states[packname][path.stem] = Data.exported

	elif path.suffix == ".state_manager":
		print(f"\tFound state manager : {path}")
		Data.state_manager = Data.exported

	else:
		Data.files[packname][path.stem + path.suffix] = content

	#if Data.exported is None:
	#	raise RuntimeError(f"Nothing were exported from {path}")

def get_pack_info(path: Path):

	with ZipFile(path) as zfile:

		for zipinfo in zfile.infolist():

			filename = zipinfo.filename

			if Path(filename).name == "index.py":

				Data.req = []

				filecontent = zfile.open(filename).read()
				exec(filecontent)

				req = Data.req[:]

				return (req,)

def load_packs(packnames):

	structure = [] # (packname, [req])

	for name in packnames:

		p = Path(name + ".zip")

		if not p.exists():
			raise RuntimeError(f"{p} not found")

		info = get_pack_info(p)
		structure.append((p.stem, info[0], p))

	loaded = set()

	while structure:

		packinfo = structure.pop(0)

		if all([r in loaded for r in packinfo[1]]):

			loaded.add(packinfo[0])
			load_pack(packinfo[2])

		else:
			structure.append(packinfo)


def main(screen):

	if Config.instance.term_size is not None:

		x, y = Config.instance.term_size
		curses.resize_term(y, x)

	else:

		y, x = screen.getmaxyx()
		Config.instance.term_size = (x, y)

	#main_state_manager = MainStateManager(screen)
	main_state_manager = Data.state_manager(screen)
	main_state_manager.init()

	screen.clear()

	#main_state_manager.push_state(screen, MainMenu)
	main_state_manager.push_state(screen, Data.states["game"]["main_menu"])

	print("Terminal size: " + str(curses.COLS) + "x" + str(curses.LINES))
	print("Window size: " + str(screen.getmaxyx()))

	prev_time = time.time()

	while main_state_manager.get_running_state():

		main_state_manager.handle_events()

		now = time.time()
		dt = now - prev_time
		prev_time = now

		main_state_manager.update(dt)
		main_state_manager.draw()
		main_state_manager.endframe()

	main_state_manager.cleanup()


def program():

	try:

		with ConfigSession():

			if not Data.save_dir.exists():
				Data.save_dir.mkdir()

			if Config.instance.term_size is None:
				print("\nDear player,")
				print("\n\t - Resize the terminal now if you want to")
				print("\tPlease note that resizing the terminal while the game is running may result in a crash")
				print("\n\t - You may also want to change keybinding,")
				print("\tin order to do that, you can edit keybinding.txt when it will be generated")

				print("\n === DISCLAIMER ==============")
				print("\t" + """
Here is the disclaimer
						""".strip())

				input("\n\nPress enter to continue")

			load_packs(Config.instance.packs)

			curses.wrapper(main)

	except Exception:

		with open(CRASH_REPORT_FILENAME, "w", encoding="utf-8") as f:
			traceback.print_exc(file=f)

		with open(CRASH_REPORT_FILENAME, "r", encoding="utf-8") as f:
			print(f.read())

		print("\nOOF, runtime error!")
		input("")

def dev_program():

	profile = cProfile.Profile()

	profile.enable()
	program()
	profile.disable()

	#profile.print_stats()

	fake_file = io.StringIO()
	stats = pstats.Stats(profile, stream=fake_file).sort_stats("cumtime")
	stats.print_stats()

	print("Logged performance analyis")

	with open("performance_analysis.txt", "w", encoding="utf-8") as file:
		file.write(fake_file.getvalue())

def production_program():

	program()


if __name__ == "__main__":

	print(f":version: {VERSION}")

	if VERSION is DEV:
		dev_program()

	elif VERSION is PRODUCTION:
		production_program()

	else:
		input(f"Unknown version: {VERSION}")
