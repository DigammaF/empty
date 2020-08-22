

from os import system, listdir
from pathlib import Path


def pack_dir(name):
	system(f"7z a -tzip {name}.zip {name}.pack\\*")

def packall():

	for name in listdir("."):

		p = Path(name)

		if p.suffix == ".pack":

			print(f"Processing {p}")

			p_comp = Path(p.stem + ".zip")

			if p_comp.exists():

				print(f"Unlinking {p_comp}")
				p_comp.unlink()

			print("Packing")

			pack_dir(p.stem)


if __name__ == "__main__":
	packall()
