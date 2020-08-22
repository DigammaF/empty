

from tkinter import Tk, Frame, Entry, Button, StringVar
from json import dumps, loads


FILE = "main.raw_space"
GENFILE = "main.space"

GAME_OBJ = 0
INDEX = 1
AREA = 2


class ToolBox(Frame):


	instance = None


	def __init__(self, root):

		ToolBox.instance = self

		Frame.__init__(self, root)

		self.mode = None

		self.entry = StringVar(self)
		Entry(self, textvariable=self.entry).grid()

		self.game_object_button_display = StringVar(self, "game object")
		Button(self, textvariable=self.game_object_button_display, command=lambda self=self: self.set_mode("game object")).grid()

		self.index_button_display = StringVar(self, "index")
		Button(self, textvariable=self.index_button_display, command=lambda self=self: self.set_mode("index")).grid()

		self.area_button_display = StringVar(self, "area")
		Button(self, textvariable=self.area_button_display, command=lambda self=self: self.set_mode("area")).grid()

		self.clear_button_display = StringVar(self, "clear")
		Button(self, textvariable=self.clear_button_display, command=lambda self=self: self.set_mode("clear")).grid()

		self.play_area_top_left_display = StringVar(self, f"{Space.instance.play_area[0]};{Space.instance.play_area[1]}")
		Button(self, textvariable=self.play_area_top_left_display, command=lambda self=self: self.set_mode("play_area_top_left")).grid()

		self.play_area_bottom_right_display = StringVar(self, f"{Space.instance.play_area[2]};{Space.instance.play_area[3]}")
		Button(self, textvariable=self.play_area_bottom_right_display, command=lambda self=self: self.set_mode("play_area_bottom_right")).grid()

	def set_mode(self, mode):

		self.mode = mode

		self.entry.set("")

		selected_clue = ["", "|"][self.mode == "game object"]
		self.game_object_button_display.set(f"{selected_clue}game object{selected_clue}")

		selected_clue = ["", "|"][self.mode == "index"]
		self.index_button_display.set(f"{selected_clue}index{selected_clue}")

		selected_clue = ["", "|"][self.mode == "area"]
		self.area_button_display.set(f"{selected_clue}area{selected_clue}")

		selected_clue = ["", "|"][self.mode == "clear"]
		self.clear_button_display.set(f"{selected_clue}clear{selected_clue}")

		selected_clue = ["", "|"][self.mode == "play_area_top_left"]
		self.play_area_top_left_display.set(f"{selected_clue}{Space.instance.play_area[0]};{Space.instance.play_area[1]}{selected_clue}")

		selected_clue = ["", "|"][self.mode == "play_area_bottom_right"]
		self.play_area_bottom_right_display.set(f"{selected_clue}{Space.instance.play_area[2]};{Space.instance.play_area[3]}{selected_clue}")

	def refresh_buttons_infos(self):

		selected_clue = ["", "|"][self.mode == "play_area_top_left"]
		self.play_area_top_left_display.set(f"{selected_clue}{Space.instance.play_area[0]};{Space.instance.play_area[1]}{selected_clue}")

		selected_clue = ["", "|"][self.mode == "play_area_bottom_right"]
		self.play_area_bottom_right_display.set(f"{selected_clue}{Space.instance.play_area[2]};{Space.instance.play_area[3]}{selected_clue}")

	def tile_selected(self, xw, yw):

		try:

			if self.mode == "game object":
				Space.instance.data[xw, yw][GAME_OBJ] = self.entry.get()

			if self.mode == "index":
				Space.instance.data[xw, yw][INDEX] = self.entry.get()

			if self.mode == "area":
				Space.instance.data[xw, yw][AREA] = self.entry.get()

			if self.mode == "clear":
				Space.instance.data[xw, yw] = [None, None, None]

			if self.mode == "play_area_top_left":
				Space.instance.play_area[0] = xw
				Space.instance.play_area[1] = yw

			if self.mode == "play_area_bottom_right":
				Space.instance.play_area[2] = xw
				Space.instance.play_area[3] = yw

		except KeyError:

			if self.mode == "game object":
				Space.instance.data[xw, yw] = [self.entry.get(), None, None]

			if self.mode == "index":
				Space.instance.data[xw, yw] = [None, self.entry.get(), None]

			if self.mode == "area":
				Space.instance.data[xw, yw] = [None, None, self.entry.get()]

		SpaceView.instance.refresh_view()


class SpaceView(Frame):


	VIEW_SIZE = 10

	instance = None


	def __init__(self, root):

		SpaceView.instance = self

		Frame.__init__(self, root)

		self.cam = [0, 0]

		self.content = Frame(self)
		self.content.grid()

		self.refresh_view()

	def refresh_view(self):

		if ToolBox.instance: ToolBox.instance.refresh_buttons_infos()

		self.content.destroy()
		self.content = Frame(self)
		self.content.grid()

		for x in range(self.VIEW_SIZE):
			for y in range(self.VIEW_SIZE):

				xw = x + self.cam[0]
				yw = y + self.cam[1]

				try:
					txt = (Space.instance.data[xw, yw][GAME_OBJ] if Space.instance.data[xw, yw][GAME_OBJ] is not None else "   ")\
					+(("," + Space.instance.data[xw, yw][INDEX]) if Space.instance.data[xw, yw][INDEX] is not None else "")\
					+(("," + Space.instance.data[xw, yw][AREA]) if Space.instance.data[xw, yw][AREA] is not None else "")

				except KeyError:
					txt = " "

				Button(self.content, text=txt, command=lambda xw=xw, yw=yw: ToolBox.instance.tile_selected(xw, yw)).grid(row=y, column=x)


class ViewMove(Frame):


	instance = None


	def __init__(self, root):

		ViewMove.instance = self

		Frame.__init__(self, root)

		Button(self, text="^", command=lambda self=self: self.move(0, -1)).grid()
		Button(self, text="v", command=lambda self=self: self.move(0, 1)).grid()
		Button(self, text="<", command=lambda self=self: self.move(-1, 0)).grid()
		Button(self, text=">", command=lambda self=self: self.move(1, 0)).grid()

	def move(self, dx, dy):

		SpaceView.instance.cam[0] += dx
		SpaceView.instance.cam[1] += dy

		SpaceView.instance.refresh_view()


class Space:


	instance = None


	def __init__(self, data, play_area):

		Space.instance = self

		self.data = data # (int, int): [game obj creation function name(str), index, area code: int]
		self.play_area = play_area # [int, int, int, int]

	def save(self):
		
		with open(FILE, "w", encoding="utf-8") as f:
			f.write(dumps({
				"data": [(k[0], k[1], v) for k, v in self.data.items() if any(i is not None for i in v)],
				"play_area": self.play_area,
			}, indent=4))

		print(f"Saved in {FILE}")

	def load(self):
		
		with open(FILE, "r", encoding="utf-8") as f:
			content = loads(f.read())

		self.data = {(i[0], i[1]): i[2] for i in content["data"]}
		self.play_area = content["play_area"]

		SpaceView.instance.refresh_view()

		print(f"Loaded from {FILE}")


BASE_GEN_CODE = """
\"\"\"
	REQ pawn.game_object, block.game_object, blit_factory.component
\"\"\"


from kernel import *


def std_pawn(x, y, state_manager):

	return Data.game_objects["game"]["pawn"](
		state_manager,
		V(x, y),
		"T",
		ColorSys.BLUE,
		Data.components["game"]["blit_factory"](cost=1, damage=1/3, travel_cost=0.05, ttl=4)
	)

def block(x, y, state_manager):
	return Data.game_objects["game"]["block"](state_manager, V(x, y))


def exported(state_manager, std_pawn=std_pawn, block=block):

	space = Space.new()

	{placeholder}
	return space


Data.exported = exported

"""


def added_line(code, line, indent=0):

	TAB = "\t"
	OPEN_P = "{"
	CLOSE_P = "}"
	return code.format(placeholder=f"{TAB*indent}{line}\n\t{OPEN_P}placeholder{CLOSE_P}")

def closed_placeholder(code):
	return code.format(placeholder="")

def generate():

	code = BASE_GEN_CODE

	for p, v in Space.instance.data.items():

		if v[GAME_OBJ] is not None:

			index = f"\"{v[INDEX]}\"" if v[INDEX] is not None else "None"
			code = added_line(code, f"space.add_game_object({v[GAME_OBJ]}({p[0]}, {p[1]}, state_manager), {index})")

	top_left_x = max(Space.instance.play_area[0], Space.instance.play_area[2])
	top_left_y = max(Space.instance.play_area[1], Space.instance.play_area[3])
	bottom_right_x = min(Space.instance.play_area[0], Space.instance.play_area[2])
	bottom_right_y = min(Space.instance.play_area[1], Space.instance.play_area[3])
	top_left = f"V({top_left_x}, {top_left_y})"
	bottom_right = f"V({bottom_right_x}, {bottom_right_y})"

	code = added_line(code, f"space.play_area = Rect({top_left}, {bottom_right})")

	code = closed_placeholder(code)

	with open(GENFILE, "w", encoding="utf-8") as f:
		f.write(code)

	print(f"Generated in {GENFILE}")


root = Tk()

Space({}, [0, 0, 0, 0])

ViewMove(root).grid(row=0, column=0)
SpaceView(root).grid(row=0, column=1)
ToolBox(root).grid(row=0, column=2)
Button(root, text="Generate", command=generate).grid(row=0, column=3)
Button(root, text="Save", command=Space.instance.save).grid(row=0, column=4)
Button(root, text="Load", command=Space.instance.load).grid(row=0, column=5)

root.mainloop()
