

import curses

from itertools import chain

from .quadtree import Quad
from .vector2d import V, Rect
from .game_object import GameObject


class Space:


	def __init__(self, data: dict,
				 register: dict=None,
				 game_objects_indexes: list=None,
				 play_area: Rect=None,
				 area_register: list=None,
				 area_map: list=None,
				 ):

		if play_area is None:
			play_area = Rect(V(0, 0), V(0, 0))

		self.play_area = play_area
		# play area is the area covered by the quadtree and pathfinding systems

		if area_register is None:
			area_register = {} # index(str): dict
			"""
			
				{
					"coords": [(int, int)],
					"facilities": [(type: str, int, int)],
					"type": str,
				}
			
			"""

		self.area_register = area_register

		if area_map is None:
			area_map = {} # (int, int): index(str)

		self.area_map = area_map

		self.data = data # (int, int): [int]

		if game_objects_indexes is None and register is not None:
			game_objects_indexes = list(register.keys())

		self.register = register # index: GameObject

		self.game_objects_indexes = [] # sorted by layer
		self.updated_objs = []

		self.static_obj_indexes = []
		self.dyn_obj_indexes = []

		for game_object_index in game_objects_indexes:
			self.add_game_object(register[game_object_index], game_object_index, index_exist_ok=True)

		self.camera = V(0, 0)

		self.static_quadtree: Quad = None
		self.dynamic_quadtree: Quad = None

		#self.updated_objs = [obj for obj in register.values() if obj.updated]
		# self.add_game_object does that already

	@classmethod
	def new(cls, register=None):

		if register is None: register = {}

		return Space(
			data={},
			register=register,
			game_objects_indexes=None,
		)

	def save(self, save_game_obj_callback=lambda index:None):
		return {
			#"data": [(k[0], k[1], v) for k, v in self.data.items()],
			"data": {},
			"register": {index: [game_obj.save(), save_game_obj_callback(index)][0] for index, game_obj in self.register.items()},
			#"game_objects_indexes": self.game_objects_indexes,
			"game_objects_indexes": [],
			"play_area": self.play_area.save(),
			"area_register": self.area_register,
			"area_map": self.area_map,
		}

	@staticmethod
	def load(saved, state_manager):
		return Space(
			#data={(i[0], i[1]): i[2] for i in saved["data"]},
			data={},
			register={index: GameObject.load(s, state_manager) for index, s in saved["register"].items()},
			#game_objects_indexes=saved["game_objects_indexes"],
			game_objects_indexes=None,
			play_area=Rect.load(saved["play_area"]),
			area_map=saved["area_map"],
			area_register=saved["area_register"],
		)

	def build_static_quadtree(self):

		self.static_quadtree = Quad(self.play_area, 10)

		for index in self.static_obj_indexes:

			obj = self.get_obj(index)
			self.static_quadtree.put(index, obj.position)

	def build_dynamic_quadtree(self):

		self.dynamic_quadtree = Quad(self.play_area, 10)

		for index in self.dyn_obj_indexes:

			obj = self.get_obj(index)
			self.dynamic_quadtree.put(index, obj.position)

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

	def add_game_object(self, game_object, index=None, index_exist_ok=False):

		game_object.space = self

		# =============================================

		if game_object.updated:
			self.updated_objs.append(game_object)

		# =============================================

		if index and index in self.register and not index_exist_ok:
			raise RuntimeError(f"Err: tried to add game object with an alreay existing index ({index})")

		if index is None:

			index = 0

			while str(index) in self.register:
				index += 1

			index = str(index)

		game_object.index = index
		self.register[index] = game_object

		[self.dyn_obj_indexes, self.static_obj_indexes][game_object.static].append(game_object.index)

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

		if obj.updated:
			self.updated_objs.remove(obj)

		[self.dyn_obj_indexes, self.static_obj_indexes][obj.static].remove(index)

		self.xunplace_game_object(obj)
		del self.register[index]
		self.game_objects_indexes.remove(index)

		obj.space = None

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

		q = Rect(self.camera, V(self.camera.x - mx + 1, self.camera.y - my + 1))

		for game_object_index in chain(self.static_quadtree.query(q), self.dynamic_quadtree.query(q)):

			game_object = self.register[game_object_index]

			if game_object.drawn:

				obj_rel_pos = reference - game_object.position

				if 0 <= obj_rel_pos.x < mx and \
						0 <= obj_rel_pos.y < my:

					try:
						game_object.draw(window, reference, obj_rel_pos)

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

		if self.static_quadtree is None:
			self.build_static_quadtree()

		self.build_dynamic_quadtree()
