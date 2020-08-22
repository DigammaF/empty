

from abc import ABC, abstractmethod
from json import dumps, loads

from .data import Data
from .config import Config


class State(ABC):


	def __init__(self, state_manager, window):

		self.state_manager = state_manager
		self.window = window

		self.defer_stack = []

	@abstractmethod
	def init(self):
		pass

	@abstractmethod
	def cleanup(self):
		pass

	@abstractmethod
	def handle_events(self):
		pass

	@abstractmethod
	def update(self, dt):
		pass

	@abstractmethod
	def draw(self):
		pass

	@abstractmethod
	def pause(self):
		pass

	@abstractmethod
	def resume(self):
		pass

	@abstractmethod
	def endframe(self):
		pass

	def defer(self, f):
		self.defer_stack.append(f)

	def do_defers(self):

		for defer in self.defer_stack:
			defer()

	def empty_defer_stack(self):
		self.defer_stack = []


class StateManager(ABC):


	def __init__(self, window):

		self.state_stack = []
		self.running = True
		self.window = window

		self.save_at_endframe = False
		self.saved = None

	@abstractmethod
	def init(self):
		pass

	@abstractmethod
	def cleanup(self):
		pass

	@property
	def current_state(self):
		return self.state_stack[-1]

	def push_state(self, window, state_cls, *args, **kwargs):

		state = state_cls(self, window, *args, **kwargs)
		state.init()
		self._push_state(state)
		return state

	def _push_state(self, state: State):

		if self.state_stack:
			self.current_state.pause()

		self.state_stack.append(state)

	def pop_state(self):

		state = self.state_stack.pop()

		if self.state_stack:
			self.current_state.resume()

		return state

	def get_running_state(self):
		return self.running

	def quit(self):
		self.running = False

	def handle_events(self):
		self.current_state.handle_events()

	def update(self, dt):
		self.current_state.update(dt)

	def draw(self):
		self.current_state.draw()

	def endframe(self):

		self.do_defers()
		self.empty_defer_stack()
		self.current_state.endframe()

		if self.save_at_endframe:

			self.save_at_endframe = False

			with open(Data.save_dir/Data.save_name, "w", encoding="utf-8") as f:
				f.write(dumps(
					{
						"saved": self.saved(),
						"packs": Config.instance.packs,
					},
					indent=2,
				))

	def get_saved_at_endframe(self):

		with open(Data.save_dir/Data.save_name, "r", encoding="utf-8") as f:

			content = loads(f.read())

			return content

	def defer(self, f):
		self.current_state.defer(f)

	def do_defers(self):
		self.current_state.do_defers()

	def empty_defer_stack(self):
		self.current_state.empty_defer_stack()
