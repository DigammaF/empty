

import curses

from string import ascii_letters


class UISystem:


	def __init__(self, state):

		self.widgets = {}
		self.state = state
		self.to_be_removed = []

	def handle_events(self):

		for widget in self.widgets.values():
			widget.handle_events()

	def update(self, dt):

		while self.to_be_removed:

			index = self.to_be_removed.pop()
			del self.widgets[index]

	def draw(self):

		for widget in self.widgets.values():
			widget.draw()

	@property
	def catch_events(self):
		"""

			Should events be handled only by the ui system?

		:return:
		"""
		return any([w.catch_events for w in self.widgets.values()])

	def add_widget(self, widget):

		widget.ui_system = self

		index = 0

		while index in self.widgets:
			index += 1

		widget.index = index
		self.widgets[index] = widget


class Widget:


	index = None
	catch_events = False # Should events be handled only by this widget?
	ui_system: UISystem = None


class TextInput(Widget):


	catch_events = True


	def __init__(self, x, y, callback, change_callback=None,
				 key_callback=None):
		"""

			callbacks can return True to invalidate the corresponding action
			(except callback)

		:param x:
		:param y:
		:param callback:
		:param change_callback: fun(new text)
		:param key_callback: fun(char, ord(char) or None)
		"""

		self.x = x
		self.y = y
		self.txt = ""
		self.callback = callback

		self.change_callback = change_callback
		self.key_callback = key_callback

	def handle_events(self):

		try:

			char = self.ui_system.state.window.getkey()

		except curses.error:  # no key pressed
			return

		o = (ord(char) if len(char) == 1 else None)

		if char == "\n":
			self.callback(self.txt)
			return

		new_txt = None

		if char == "KEY_DC" or o == 8:
			new_txt = self.txt[:-1]

		if (char in ascii_letters or o == 32) and ((self.key_callback is None) or not self.key_callback(char, o)):
			new_txt = self.txt + char

		if (new_txt is not None) and ((self.change_callback is None) or not self.change_callback(new_txt)):
			self.txt = new_txt

	def draw(self):
		self.ui_system.state.window.addstr(self.y, self.x, self.txt + "|")

	def remove(self):
		self.ui_system.to_be_removed.append(self.index)

	def set_active(self, flag):
		self.catch_events = flag
