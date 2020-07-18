

import curses

from .vector2d import V


class Space:


	def __init__(self, data: dict,
				 register: dict=None,
				 game_objects_indexes: list=None):

		self.data = data # (int, int): [int]

		if game_objects_indexes is None and register is not None:
			game_objects_indexes = register.keys()[:]

		self.register = register # index: GameObject

		self.game_objects_indexes = [] # sorted by layer

		for game_object_index in game_objects_indexes:
			self.add_game_object(register[game_object_index], game_object_index)

		self.camera = V(0, 0)

		self.updated_objs = [obj for obj in register.values() if obj.updated]

	@classmethod
	def new(cls):
		return Space(
			data={},
			register={},
			game_objects_indexes=[],
		)

	def is_walkable(self, x, y=None):

		if isinstance(x, V): return self.is_walkable(x.x, x.y)
		if y is None: raise RuntimeError

		indexes = self.get_indexes_at(x, y)

		return all([self.register[index].is_walkable() for index in indexes])

	def get_walk_cost(self, x, y=None):

		if isinstance(x, V): return self.get_walk_cost(x.x, x.y)
		if y is None: raise RuntimeError

		indexes = self.get_indexes_at(x, y)

		return sum([self.register[index].get_walk_cost() for index in indexes])

	def focus_on(self, v, mx, my):

		self.camera.set(V(v.x + mx//2, v.y + my//2))
		#self.camera.set(v)

	def get_obj(self, index):
		return self.register[index]

	def set_obj(self, index, obj):
		self.register[index] = obj

	def get_indexes_at(self, x, y=None):

		if isinstance(x, V): return self.get_indexes_at(x.x, x.y)
		if y is None: raise RuntimeError

		try:
			return self.data[x, y]

		except KeyError:
			self.data[x, y] = []
			return self.data[x, y]

	def add_game_object(self, game_object, index=None):

		game_object.space = self

		if game_object.updated:
			self.updated_objs.append(game_object)

		if index and index in self.register:
			raise RuntimeError(f"Err: tried to add game object with an alreay existing index ({index})")

		if index is None:

			index = 0

			while index in self.register:
				index += 1

		game_object.index = index
		self.register[index] = game_object

		for i in range(len(self.game_objects_indexes)):

			if self.get_obj(self.game_objects_indexes[i]).layer >= game_object.layer:
				self.game_objects_indexes.insert(i, index)
				break

		else:
			self.game_objects_indexes.append(index)

		self.xplace_game_object(game_object)

		return index

	def rem_game_object(self, index):

		obj = self.register[index]

		obj.space = None

		if obj.updated:
			self.updated_objs.remove(obj)

		self.xunplace_game_object(obj)
		del self.register[index]
		self.game_objects_indexes.remove(index)

	def place_game_object(self, index, x, y=None):

		if isinstance(x, V): self.place_game_object(index, x.x, x.y); return
		if y is None: raise RuntimeError

		self.get_indexes_at(x, y).append(index)

	def xplace_game_object(self, obj):
		self.place_game_object(obj.index, obj.position)

	def unplace_game_object(self, index, x, y=None):

		if isinstance(x, V): self.unplace_game_object(index, x.x, x.y); return
		if y is None: raise RuntimeError

		self.get_indexes_at(x, y).remove(index)

	def xunplace_game_object(self, obj):
		self.unplace_game_object(obj.index, obj.position)

	def draw(self, window, reference=None):

		reference = reference or self.camera

		my, mx = window.getmaxyx()

		for game_object_index in self.game_objects_indexes:

			game_object = self.register[game_object_index]

			if game_object.drawn:

				obj_rel_pos = reference - game_object.position

				if 0 <= obj_rel_pos.x < mx and \
						0 <= obj_rel_pos.y < my:

					try:
						game_object.draw(window, reference)

					except curses.error:
						pass
						#traceback.print_exc()

	def compute_collisions(self, game_object, position):

		for index in self.get_indexes_at(position):

			if index != game_object.index:

				other_obj = self.get_obj(index)

				game_object.collision(other_obj)
				other_obj.collision(game_object)

	def compute_collision_enter(self, game_object, position):

		for index in self.get_indexes_at(position):

			other_obj = self.get_obj(index)

			if not other_obj.is_walkable():

				game_object.collision_enter(other_obj)
				other_obj.collision_enter(game_object)

	def relocate(self, game_object, new_position):

		self.xunplace_game_object(game_object)
		game_object.position.set(new_position)
		self.xplace_game_object(game_object)

	def update(self, dt):

		for obj in self.updated_objs:
			obj.update(dt)
