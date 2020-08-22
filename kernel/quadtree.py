

from .vector2d import Rect, V


OBJ = 0
POS = 1


class Quad:


	def __init__(self, rect: Rect, limit: int, redistribute_on_split=False):

		self.rect = rect
		self.limit = limit
		self.redistribute_on_split = redistribute_on_split

		self.recs = [] # (obj, pos: V)

		self.split = False

		self.nw_quad = None
		self.ne_quad = None
		self.sw_quad = None
		self.se_quad = None

		self.quads = tuple()

	def _create_child_quad(self, rect: Rect):
		return Quad(rect=rect, limit=self.limit, redistribute_on_split=self.redistribute_on_split)

	def _debug_split_amount(self):

		if self.split:
			return 1\
				   + self.nw_quad._debug_split_amount()\
				   + self.ne_quad._debug_split_amount()\
				   + self.se_quad._debug_split_amount()\
				   + self.sw_quad._debug_split_amount()

		else:
			return 0

	def overlap(self, rect: Rect):
		return self.rect.overlap(rect)

	def inside(self, v: V):
		return self.rect.is_inside(v)

	def put(self, obj, pos: V):

		if not self.split:

			if len(self.recs) == self.limit:
				self.do_split()

			else:
				self.recs.append((obj, pos))
				return

		if self.split:

			for quad in self.quads:
				if quad.inside(pos):
					quad.put(obj, pos)
					return

	def query(self, rect: Rect):

		for rec in self.recs:
			if rect.is_inside(rec[POS]):
				yield rec[OBJ]

		if self.split:
			for quad in self.quads:
				if quad.overlap(rect):
					for obj in quad.query(rect):
						yield obj

	def do_split(self):

		# = set split

		self.split = True

		# = create ne, nw, se, sw

		middle = V(
			(self.rect.top_left.x + self.rect.bottom_right.x)/2,
			(self.rect.top_left.y + self.rect.bottom_right.y)/2,
		)

		self.ne_quad = self._create_child_quad(Rect(
			top_left=V((self.rect.top_left.x + self.rect.bottom_right.x)/2, self.rect.top_left.y),
			bottom_right=V(self.rect.bottom_right.x, (self.rect.top_left.y + self.rect.bottom_right.y)/2),
		))

		self.nw_quad = self._create_child_quad(Rect(
			top_left=self.rect.top_left,
			bottom_right=middle,
		))

		self.se_quad = self._create_child_quad(Rect(
			top_left=middle,
			bottom_right=self.rect.bottom_right,
		))

		self.sw_quad = self._create_child_quad(Rect(
			top_left=V(self.rect.top_left.x, (self.rect.top_left.y + self.rect.bottom_right.y)/2),
			bottom_right=V((self.rect.top_left.x + self.rect.bottom_right.x)/2, self.rect.bottom_right.y),
		))

		# = create quads

		self.quads = (self.ne_quad, self.nw_quad, self.se_quad, self.sw_quad)

		# = redistribute (relies on self.split = True)

		if self.redistribute_on_split:
			while self.recs:
				rec = self.recs.pop()
				self.put(rec[OBJ], rec[POS])
