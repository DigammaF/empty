

from pathlib import Path
from os import listdir


class Data:


	components = {}
	states = {}
	spaces = {}
	game_objects = {}
	files = {}
	state_manager = None

	exported = None
	req = None

	save_dir = Path("saves")
	save_name = None # str


	@staticmethod
	def saves():

		for name in listdir(str(Data.save_dir)):
			yield Data.save_dir/name

	@staticmethod
	def save_path(save_name: str):
		return Data.save_dir/save_name
