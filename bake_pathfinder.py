

from pathlib import Path


PACKS = ["game"]
SPACE_PACKNAME = "game"
SPACE_NAME = "stresstest"

outfile = Path("game_space_maker") / (SPACE_NAME + ".pathfinder_data")


from main import load_packs
from kernel import Data, Pathfinder
from json import dumps


load_packs(PACKS)
space = Data.spaces[SPACE_PACKNAME][SPACE_NAME]
pathfinder = Pathfinder.new(space)
pathfinder.compute_paths(lambda p: print(f"{(p*100):.2f}"))

with open(outfile, "w", encoding="utf-8") as f:
	f.write(dumps(pathfinder.save(), indent=4))
