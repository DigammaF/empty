

from .vector2d import V
from .data import Data


class Component:


	updated = False
	drawn = False
	walkable = True # can other game objects walk through this?
	walk_cost = 0

	custom_menu = None # A State class. Can't be changed

	NAME = "name"
	name = None
	PACKNAME = "packname"
	packname = None


	def __init__(self):

		self.position = V(0, 0)
		self.game_object = None
		self.state_manager = None

	@classmethod
	def blank(cls):
		return cls()

	def save(self):
		return {
			"position": self.position.save(),
			"updated": self.updated,
			"drawn": self.drawn,
			"walkable": self.walkable,
			"walk_cost": self.walk_cost,
			Component.NAME: self.name,
			Component.PACKNAME: self.packname,
			**self.save_custom(),
		}

	def save_custom(self):
		return {}

	@staticmethod
	def load(saved):

		obj = Data.components[saved[Component.PACKNAME]][saved[Component.NAME]].blank()

		obj.position = V.load(saved["position"])
		obj.updated = saved["updated"]
		obj.drawn = saved["drawn"]
		obj.walkable = saved["walkable"]
		obj.walk_cost = saved["walk_cost"]

		obj.name = saved[Component.NAME]
		obj.packname = saved[Component.PACKNAME]

		obj.load_custom(saved)

		return obj

	def load_custom(self, saved):
		pass

	def attach(self, game_object):

		self.game_object = game_object
		self.state_manager = game_object.state_manager
		self.position.reference = game_object.position

	def get_relative_position(self, reference):
		return reference - self.position

	def update(self, dt):
		pass

	def draw(self, window, reference, relative_position):
		pass

	# ======= EVENTS ========================

	def is_collected(self, game_obj_index):
		pass

	def collision(self, game_obj_index):
		pass

	def collision_enter(self, game_obj_index):
		"""

			triggered when self.game_object tries to walk on non walkable.
			the game_obj is stopped, but collision_enter is triggered with
			game_obj being all non walkable game_obj

			non walkable game_obj also receive a collision_enter event

		:return:
		"""
		pass

	def dies(self):
		pass

	def is_killed(self, game_obj_index):
		pass

	def is_hit(self, game_obj_index):
		pass


class GameObject:
	"""

		A Game Object can't modify it's component dict!

	"""


	BLIT_FACTORY = "blit_factory"
	LEGS = "legs"


	layer = 0 # Don't change it at runtime!

	index = None
	space = None
	ap = 0
	health = 1 # 0-1
	alive = True
	energy = 1 # 0-1


	class NoSuchComponent(Exception): pass


	def __init__(self, name, state_manager, position, components: dict,
				 static: bool=False):

		self.name = name
		self.state_manager = state_manager
		self.position = position
		self.velocity = V(0, 0)
		self.blit_com = V(0, 0)
		self.components = components # cls or str: instance
		self.static = static # for the love of god, never change this at runtime!
		self.updated = any([component.updated for component in components.values()])
		self.drawn = any([component.drawn for component in components.values()])

		self.updated_components = [component for component in components.values() if component.updated]
		self.drawn_components = [component for component in components.values() if component.drawn]

		for component in self.components.values():
			component.attach(self)

	def __str__(self):
		return f"{self.name}"

	def save(self):
		return {
			"layer": self.layer,
			"index": self.index,
			"ap": self.ap,
			"health": self.health,
			"alive": self.alive,
			"energy": self.energy,

			"name": self.name,
			"position": self.position.save(),
			"velocity": self.velocity.save(),
			"blit_com": self.blit_com.save(),
			"components": {i: c.save() for i, c in self.components.items()},
			"static": self.static,
		}

	@staticmethod
	def load(saved, state_manager):

		obj = GameObject(
			name=saved["name"],
			state_manager=state_manager,
			position=V.load(saved["position"]),
			components={i: Component.load(s) for i, s in saved["components"].items()},
			static=saved["static"],
		)

		obj.velocity = V.load(saved["velocity"])
		obj.blit_com = V.load(saved["blit_com"])

		return obj

	def is_walkable(self):
		return all([component.walkable for component in self.components.values()])

	def get_walk_cost(self):
		return sum([component.walk_cost for component in self.components.values()])

	def is_collectable(self):
		return any([component.collectable for component in self.components.values()])

	def update(self, dt):

		self.update_position()
		self.handle_blit_com()

		for component in self.updated_components:
			component.update(dt)

	def draw(self, window, reference, relative_position):

		for component in self.drawn_components:
			component.draw(window, reference, relative_position)

	def get_component(self, k):

		try:
			return self.components[k]

		except KeyError:
			raise GameObject.NoSuchComponent

	@property
	def has_ap(self):
		return self.ap == 0

	def damage(self, v, origin_index):

		if self.alive:

			self.health -= v
			self.is_hit(origin_index)

			if self.health <= 0:

				self.alive = False
				self.is_killed(origin_index)

	# ========== SPACE DEPENDENT ==============

	@property
	def exists(self):
		return self.space is not None

	def vanish(self):
		if self.exists: self.space.rem_game_object(self.index)

	def update_position(self):
		"""

		legs.base_walk_cost must be a float

		:return:
		"""

		if self.has_ap and self.velocity:

			new_position = self.position + self.velocity

			try:
				base_walk_cost = self.get_component(GameObject.LEGS).base_walk_cost

			except GameObject.NoSuchComponent:
				base_walk_cost = 0

			if self.space.is_walkable(new_position):

				self.ap += self.space.get_walk_cost(new_position) + \
								  base_walk_cost

				self.space.compute_collisions(self, new_position)

				self.space.relocate(self, new_position)

			else:

				self.space.compute_collision_enter(self, new_position)

			self.velocity.nullify()

	def handle_blit_com(self):
		"""

		blit_factory.new_blit is supposed to be (position=, direction=): GameObject()

		:return:
		"""

		if self.has_ap and self.blit_com:

			try:
				blit_factory = self.get_component(GameObject.BLIT_FACTORY)

			except GameObject.NoSuchComponent:
				return

			self.ap += blit_factory.cost

			position = (self.position + self.blit_com).copy
			blit = blit_factory.new_blit(position=position, direction=self.blit_com.copy)
			self.space.add_game_object(blit)

			self.space.compute_collisions(blit, position)

			self.blit_com.nullify()

	# ========== EVENTS =======================

	def collision(self, game_obj):

		for component in self.components.values():
			component.collision(game_obj)

	def collision_enter(self, game_obj):

		for component in self.components.values():
			component.collision_enter(game_obj)

	def is_collected(self, game_obj):

		for component in self.components.values():
			component.is_collected(game_obj)

	def dies(self):

		for component in self.components.values():
			component.dies()

	def is_killed(self, game_obj_index):

		for component in self.components.values():
			component.is_killed(game_obj_index)

	def is_hit(self, game_obj_index):

		for component in self.components.values():
			component.is_hit(game_obj_index)
