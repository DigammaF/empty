

import curses


class ColorSys:


	BLACK = curses.COLOR_BLACK
	RED = curses.COLOR_RED
	GREEN = curses.COLOR_GREEN
	YELLOW = curses.COLOR_YELLOW
	BLUE = curses.COLOR_BLUE
	MAGENTA = curses.COLOR_MAGENTA
	CYAN = curses.COLOR_CYAN
	WHITE = curses.COLOR_WHITE


	def __init__(self):

		self.pairs = {(curses.COLOR_WHITE, curses.COLOR_BLACK): 0} # (int, int): int

	def get_color(self, foreground, background):

		if (foreground, background) in self.pairs:
			return curses.color_pair(self.pairs[(foreground, background)])

		else:
			i = len(self.pairs)
			self.pairs[(foreground, background)] = i
			curses.init_pair(i, foreground, background)
			return curses.color_pair(i)
