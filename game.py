

import curses

from kernel import State, StateManager, ColorSys,\
	GameObject, Component, Space, V


# =================== STATES =====================================


class MainMenu(State):


	def init(self):

		self.resume()

	def cleanup(self):
		pass

	def handle_events(self):

		try:

			char = self.window.getkey()

		except curses.error: # no key pressed
			return

		print(f": ({ord(char)}) {char}")

		if char == "q":
			self.state_manager.quit()

		if char == "n":
			self.state_manager.push_state(self.window, MainGame)

	def update(self, dt):
		pass

	def draw(self):
		pass

	def pause(self):
		pass

	def resume(self):

		curses.curs_set(False)
		self.window.nodelay(True)

		self.window.bkgd(" ", self.state_manager.color_sys.get_color(
			ColorSys.WHITE,
			ColorSys.BLACK,
		))

		self.window.attrset(self.state_manager.color_sys.get_color(
			ColorSys.WHITE,
			ColorSys.BLACK,
		))

		my, mx = self.window.getmaxyx()

		self.window.border()
		self.window.addstr(int(my * 0.3), int(mx * 0.3), "Empty")

		y, x = int(my * 0.3) + 2, int(mx * 0.32)

		self.window.addstr(y + 2, x, " ouveau")
		self.window.addstr(y + 2, x, "N", curses.A_BOLD | curses.A_UNDERLINE)
		self.window.addstr(y + 3, x, " uitter")
		self.window.addstr(y + 3, x, "Q", curses.A_BOLD | curses.A_UNDERLINE)
		self.window.addstr(y + 4, x, " rédits")
		self.window.addstr(y + 4, x, "C", curses.A_BOLD | curses.A_UNDERLINE)

		self.window.refresh()

	def endframe(self):
		pass


class MainGame(State):


	def init(self):

		self.space = get_debug_space(self.state_manager)
		self.dt_hist = []
		self.dt_hist_size = 300

		self.resume()

	def cleanup(self):
		pass

	def handle_events(self):

		try:

			char = self.window.getkey()

		except curses.error: # no key pressed
			return

		if char == "\n":
			my, mx = self.window.getmaxyx()
			return

		if char == "k":
			self.state_manager.quit()
			return

		if char == "z":
			self.space.get_obj("player").velocity.set(V(0, 1))
			return

		if char == "s":
			self.space.get_obj("player").velocity.set(V(0, -1))
			return

		if char == "q":
			self.space.get_obj("player").velocity.set(V(1, 0))
			return

		if char == "d":
			self.space.get_obj("player").velocity.set(V(-1, 0))
			return

		if char == "8":
			self.space.get_obj("player").blit_com.set(V(0, 1))
			return

		if char == "2":
			self.space.get_obj("player").blit_com.set(V(0, -1))
			return

		if char == "4":
			self.space.get_obj("player").blit_com.set(V(1, 0))
			return

		if char == "6":
			self.space.get_obj("player").blit_com.set(V(-1, 0))
			return

	def update(self, dt):

		self.space.update(dt)

		self.dt_hist.append(dt)

		while len(self.dt_hist) >= self.dt_hist_size:
			del self.dt_hist[0]

	def draw(self):

		my, mx = self.window.getmaxyx()

		self.space.focus_on(self.space.get_obj("player").position, mx, my)

		self.window.clear()
		self.space.draw(self.window)

		a = (sum(self.dt_hist)/len(self.dt_hist))
		self.window.addstr(0, 0, str(5*(int(1/a)//5) if a != 0 else "x"))

	def pause(self):
		pass

	def resume(self):

		curses.curs_set(False)
		self.window.nodelay(True)

		self.window.clear()

		self.window.bkgd(" ", self.state_manager.color_sys.get_color(
			ColorSys.WHITE,
			ColorSys.BLACK,
		))

		self.window.attrset(self.state_manager.color_sys.get_color(
			ColorSys.WHITE,
			ColorSys.BLACK,
		))

	def endframe(self):

		self.window.refresh()


class MainStateManager(StateManager):


	def init(self):

		self.color_sys = ColorSys()

	def cleanup(self):
		pass


#====================== COMPONENTS =================================


class APRefill(Component):


	updated = True


	def __init__(self, f: int or float=1.0):

		super().__init__()

		self.f = f

	def update(self, dt):

		self.game_object.ap = max(0, self.game_object.ap - dt*self.f)


class MonoEngine(Component):


	updated = True


	def __init__(self, direction, owner, damage, ttl):

		super().__init__()

		self.direction = direction
		self.owner = owner
		self.damage = damage
		self.ttl = ttl

	def update(self, dt):

		self.ttl -= dt

		if self.ttl < 0:
			self.defer_vanish()
			return

		self.game_object.velocity.set(self.direction)

	def collision(self, game_obj):

		if game_obj.name == "pawn":
			game_obj.damage(self.damage, self.owner)

		self.defer_vanish()

	def collision_enter(self, game_obj):

		self.defer_vanish()

	def defer_vanish(self):
		self.game_object.state_manager.defer(lambda self=self: self.game_object.vanish())


class Sprite(Component):


	drawn = True


	def __init__(self, char, fg, bg=ColorSys.BLACK):

		super().__init__()

		self.fg = fg
		self.bg = bg
		self.char = char

	def draw(self, window, reference):

		p = self.get_relative_position(reference)

		window.addstr(p.y, p.x, self.char, self.state_manager.color_sys.get_color(
			self.fg,
			self.bg,
		))


class Bloc(Component):


	walkable = False


class TextDisplay(Component):


	drawn = True
	updated = True


	def __init__(self, y_offset):

		super().__init__()

		self.position.set(0, y_offset)

		self.buffer = [] # (ttl, str)

	@property
	def text(self):

		if self.buffer:
			return self.buffer[0][1]

		else:
			return None

	def push_text(self, text, ttl=None):

		if ttl is None:
			word_count = len(text.split(" "))
			ttl = word_count + 0.1*word_count

		self.buffer.append([ttl, text])

	def update(self, dt):

		if self.buffer:

			self.buffer[0][0] -= dt

			if self.buffer[0][0] <= 0:
				del self.buffer[0]

	def draw(self, window, reference):

		if self.text:

			p = self.get_relative_position(reference)
			my, mx = window.getmaxyx()

			if 0 <= p.y < my:

				start_x = p.x - len(self.text)//2

				str_start_x = max(0, -start_x)
				str_end_x = min(len(self.text), mx - max(0, start_x))

				self.game_object.state_manager.defer(lambda x=max(0, start_x), y=p.y, t=self.text[str_start_x:str_end_x], window=window: window.addstr(y, x, t))


class BlitFactory(Component):


	def __init__(self, damage, cost, travel_cost, ttl):

		super().__init__()

		self.damage = damage
		self.cost = cost
		self.travel_cost = travel_cost
		self.ttl = ttl

	def new_blit(self, position, direction):
		return new_blit(
			state_manager=self.state_manager,
			owner=self.game_object,
			position=position,
			damage=self.damage,
			direction=direction,
			ttl=self.ttl,
			travel_cost=self.travel_cost,
		)


class Legs(Component):


	def __init__(self, base_walk_cost):

		super().__init__()

		self.base_walk_cost = base_walk_cost


class Inventory(Component):


	pass


#====================== GAME OBJECTS ===============================


def new_pawn(state_manager, position, char, color, blit_factory_component=None, components=None):

	if components is None:
		components = {}

	obj_components = {
		APRefill: APRefill(1),
		Sprite: Sprite(char, color),
		"name_display": TextDisplay(-1),
		"dialog_display": TextDisplay(1),
		GameObject.LEGS: Legs(0.1),
		**components,
	}

	if blit_factory_component is not None:
		obj_components[GameObject.BLIT_FACTORY] = blit_factory_component

	return GameObject(
		name="pawn",
		state_manager=state_manager,
		position=position,
		components=obj_components,
	)

def new_block(state_manager, position, components=None):

	if components is None:
		components = {}

	return GameObject(
		name="bloc",
		state_manager=state_manager,
		position=position,
		components={
			Bloc: Bloc(),
			Sprite: Sprite("#", ColorSys.YELLOW),
			**components,
		},
		static=True,
	)

def new_blit(state_manager, owner, position, direction, damage, ttl, travel_cost,
			 components=None):

	if components is None:
		components = {}

	return GameObject(
		name="blit",
		state_manager=state_manager,
		position=position,
		components={
			MonoEngine: MonoEngine(
				direction=direction, owner=owner, damage=damage, ttl=ttl
			),
			Sprite: Sprite("o", ColorSys.RED),
			APRefill: APRefill(1),
			GameObject.LEGS: Legs(travel_cost),
			**components,
		}
	)


#====================== MAP ========================================


def get_debug_space(state_manager):

	space = Space.new()

	space.add_game_object(new_pawn(
		state_manager,
		V(0, 0),
		"T",
		ColorSys.BLUE,
		BlitFactory(cost=1, damage=1/3, travel_cost=0.05, ttl=4),
	), "player")

	for p in (V(-1, -1), V(-1, 1), V(1, 1), V(1, -1)):
		space.add_game_object(new_block(state_manager, p))

	space.add_game_object(new_block(state_manager, V(2, 2)))

	return space
