

from __future__ import annotations

from pathlib import Path
from json import dump, load


class ConfigSession:


	def __enter__(self):

		if Config.instance is not None:
			raise RuntimeError("Unable to nest Config instances")

		if Config.path.exists():

			saved = load(open(Config.path, "r", encoding="utf-8"))

			Config.instance = Config(
				term_size=tuple(saved["term_size"]) if saved["term_size"] else None,
				packs=saved["packs"],
				custom=saved["custom"],
				keybinding=None,
			)

		else:
			Config.instance = Config()

		return Config.instance

	def __exit__(self, exc_type, exc_val, exc_tb):

		dump({
			"term_size": Config.instance.term_size,
			"packs": Config.instance.packs,
			"custom": Config.instance.custom,
		}, open(Config.path, "w", encoding="utf-8"), indent=4)


class Config:


	path = Path("config.txt")
	keybinding_path = Path("keybinding.txt")
	instance: Config = None


	def __init__(self,
				 term_size=None,
				 packs=None,
				 custom=None,
				 keybinding=None,
				 colors=False,
				 ):

		if packs is None:
			packs = ["game"]

		if custom is None:
			custom = {}

		if keybinding is None:

			keybinding = {
				"kuit game": "k",
				"move up": "z",
				"move down": "s",
				"move right": "d",
				"move left": "q",
				"blit up": "8",
				"blit down": "2",
				"blit right": "6",
				"blit left": "4",
				"components menu": "m",
			}

		if not Config.keybinding_path.exists():

			with open(Config.keybinding_path, "w", encoding="utf-8") as f:
				f.write("\n".join([f"{k}:{v}" for k, v in keybinding.items()]))

		else:

			with open(Config.keybinding_path, "r", encoding="utf-8") as f:

				for line in f.readlines():

					data = line.strip().split(":")
					keybinding[data[0]] = data[1]

		self.term_size = term_size # (int x, int y)
		self.packs = packs

		self.custom = custom # {pack name: {}}

		self.keybinding = keybinding

		self.colors = colors
