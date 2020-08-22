
from __future__ import annotations

from math import sqrt, fabs


class V:
	"""

		References aren't saved!

	"""


	def __init__(self, x, y, reference=None):

		if isinstance(x, V):
			self.__init__(x.x, x.y, x.reference)
			return

		self.reference = reference

		self._x = x
		self._y = y

		self.length_cache = None

	def save(self):
		return {"x": self._x, "y": self._y}

	@staticmethod
	def load(saved):
		return V(saved["x"], saved["y"])

	def distance(self, other):
		return fabs(self.x - other.x) + fabs(self.y - other.y)

	@property
	def copy(self):
		return V(self.x, self.y, (self.reference.copy if self.reference is not None else None))

	def set(self, x, y=None):

		if isinstance(x, V):
			self.set(x.x, x.y)
			return

		if y is None:
			raise RuntimeError(str(x))

		self._x = x
		self._y = y

		self.length_cache = None

	@property
	def x(self):
		return self._x if self.reference is None else self._x + self.reference.x

	@property
	def y(self):
		return self._y if self.reference is None else self._y + self.reference.y

	@property
	def length(self):
		"""

			local length

		"""

		self.length_cache = self.length_cache or sqrt(self.x**2 + self.y**2)
		return self.length_cache

	def sized(self, l):

		f = l/self.length
		v = V(self.x*f, self.y*f, self.reference)
		v.length_cache = l

		return v

	def nullify(self):

		self._x = 0
		self._y = 0

		self.length_cache = 0

	def __add__(self, other):
		return V(self.x + other.x, self.y + other.y, self.reference)

	def __sub__(self, other):
		return V(self.x - other.x, self.y - other.y, self.reference)

	def __bool__(self):
		return bool(self.x) or bool(self.y)

	def __eq__(self, other: V):
		return self.x == other.x and self.y == other.y

	def __str__(self):

		if self.reference is not None:
			return f"({self._x};{self._y})[{self.reference}]:({self.x};{self.y})"

		else:
			return f"|{self._x};{self._y}|"


class Rect:


	def __init__(self, top_left, bottom_right):

		self.top_left = top_left
		self.bottom_right = bottom_right

	def __str__(self):
		return f"({self.top_left} -> {self.bottom_right})"

	def save(self):
		return {
			"top_left": self.top_left.save(),
			"bottom_right": self.bottom_right.save(),
		}

	@classmethod
	def load(cls, saved):
		return Rect(
			top_left=V.load(saved["top_left"]),
			bottom_right=V.load(saved["bottom_right"]),
		)

	def is_inside(self, v: V):
		return self.top_left.x >= v.x >= self.bottom_right.x\
			and self.top_left.y >= v.y >= self.bottom_right.y

	def overlap(self, rect: Rect):

		if self.top_left.x <= rect.bottom_right.x or rect.top_left.x <= self.bottom_right.x:
			return False

		if self.top_left.y <= rect.bottom_right.y or rect.top_left.y <= self.bottom_right.y:
			return False

		return True

	def coords(self):

		for x in range(int(self.top_left.x), int(self.bottom_right.x) + 1):
			for y in range(int(self.bottom_right.y), int(self.top_left.y) + 1):
				yield x, y
