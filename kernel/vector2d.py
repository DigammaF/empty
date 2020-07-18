

from math import sqrt


class V:


	def __init__(self, x, y, reference=None):

		if isinstance(x, V):
			self.__init__(x.x, x.y, x.reference)
			return

		self.reference = reference

		self._x = x
		self._y = y

		self.length_cache = None

	@property
	def copy(self):
		return V(self.x, self.y, (self.reference.copy if self.reference is not None else None))

	def set(self, x, y=None):

		if isinstance(x, V):
			self.set(x.x, x.y)
			return

		if y is None:
			raise RuntimeError

		self._x = x
		self._y = y

		self.length_cache = None

	@property
	def x(self):
		return self._x + (self.reference.x if self.reference is not None else 0)

	@property
	def y(self):
		return self._y + (self.reference.y if self.reference is not None else 0)

	@property
	def length(self):

		self.length_cache = self.length_cache or sqrt(self.x**2 + self.y**2)
		return self.length_cache

	def sized(self, l):

		f = l/self.length
		return V(self.x*f, self.y*f, self.reference)

	def nullify(self):

		self._x = 0
		self._y = 0

	def __add__(self, other):
		return V(self.x + other.x, self.y + other.y, self.reference)

	def __sub__(self, other):
		return V(self.x - other.x, self.y - other.y, self.reference)

	def __bool__(self):
		return bool(self.x) or bool(self.y)

	def __str__(self):

		if self.reference is not None:
			return f"({self._x};{self._y})[{self.reference}]:({self.x};{self.y})"

		else:
			return f"|{self._x};{self._y}|"
