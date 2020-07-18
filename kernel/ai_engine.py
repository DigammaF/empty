

from json import load, dump

from pyswip import Prolog


class AIEngine:


	COM_TYPE_ASSERTZ = 0
	COM_TYPE_RETRACT = 1


	def __init__(self):

		self.history = [] # [{"com": int, "data": str}]
		self.prolog = None

	def _debug_save_in(self, filename):
		dump(self.history, filename)

	def _debug_load_from(self, filename):

		history = load(filename)
		self.init(history)

	def init(self, history):

		self._init_prolog()

		for fact in history:
			self.ack_fact(fact["com"], fact["data"])

	def _init_prolog(self):

		if self.prolog is not None:
			raise RuntimeError("Il a été demandé d'initialiser une nouvelle instance de prolog, ce qui est impossible sans relancer l'application")

		self.prolog = Prolog()

	def ack_fact(self, com, data):

		self.history.append({"com": com, "data": data})

		if com == AIEngine.COM_TYPE_ASSERTZ:
			self.prolog.assertz(data)

		elif com == AIEngine.COM_TYPE_RETRACT:
			self.prolog.retract(data)

	def assertz(self, data):
		self.ack_fact(AIEngine.COM_TYPE_ASSERTZ, data)

	def retract(self, data):
		self.ack_fact(AIEngine.COM_TYPE_RETRACT, data)
