

from .vector2d import V


class Component:
	"""

		A component can't modify his physics attributes!

	"""


	updated = False
	drawn = False
	walkable = True # can other game objects walk through this?
	walk_cost = 0
	collectable = False


	def __init__(self):

		self.position = V(0, 0)
		self.game_object = None
		self.state_manager = None

	def attach(self, game_object):

		self.game_object = game_object
		self.state_manager = game_object.state_manager
		self.position.reference = game_object.position

	def get_relative_position(self, reference):
		return reference - self.position

	def update(self, dt):
		pass

	def draw(self, window, reference):
		pass

	# ======= EVENTS ========================

	def is_collected(self, game_obj):
		pass

	def collision(self, game_obj):
		pass

	def collision_enter(self, game_obj):
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

	def is_killed(self, game_obj):
		pass

	def is_hit(self, game_obj):
		pass


class GameObject:
	"""

		A Game Object can't modify it's component dict!

	"""


	BLIT_FACTORY = "blit_factory"
	LEGS = "legs"


	layer = 0

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
		self.static = static
		self.updated = any([component.updated for component in components.values()])
		self.drawn = any([component.drawn for component in components.values()])

		self.updated_components = [component for component in components.values() if component.updated]
		self.drawn_components = [component for component in components.values() if component.drawn]

		for component in self.components.values():
			component.attach(self)

	def __str__(self):
		return f"{self.name}"

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

	def draw(self, window, reference):

		for component in self.drawn_components:
			component.draw(window, reference)

	def get_component(self, k):

		try:
			return self.components[k]

		except KeyError:
			raise GameObject.NoSuchComponent

	@property
	def has_ap(self):
		return self.ap == 0

	def damage(self, v, origin):

		if self.alive:

			self.health -= v
			self.is_hit(origin)

			if self.health <= 0:

				self.alive = False
				self.is_killed(origin)

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

	def is_killed(self, game_obj):

		for component in self.components.values():
			component.is_killed(game_obj)

	def is_hit(self, game_obj):

		for component in self.components.values():
			component.is_hit(game_obj)
