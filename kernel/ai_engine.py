

from __future__ import annotations
from json import load, dump

from pyswip import Prolog


class AIEngine:


	instance: AIEngine = None

	COM_TYPE_ASSERTZ = 1
	COM_TYPE_RETRACT = 0


	def __init__(self):

		self.history = [] # [{"com": int, "data": str}]
		self.prolog = None

		if AIEngine.instance is not None:

			self.history = AIEngine.instance.history
			self.prolog = AIEngine.instance.prolog

		else:
			AIEngine.instance = self

		self.init({})

	def _debug_save_in(self, file):

		if isinstance(file, str): file = open(file, "w", encoding="utf-8")

		dump(self.history, file)

	def _debug_load_from(self, file):

		if isinstance(file, str): file = open(file, "r", encoding="utf-8")

		history = load(file)
		self.init(history)

	def save(self):
		return {
			"history": AIEngine.cleaned_history(self.history),
		}

	@staticmethod
	def load(saved):

		obj = AIEngine()
		obj.init(saved["history"])

		return obj

	@staticmethod
	def cleaned_history(history):

		r_history = history[:]
		i = 0

		while i < len(r_history):

			fact = r_history[i]

			if fact["com"] == AIEngine.COM_TYPE_RETRACT:

				del r_history[i]

				r_history.remove({
					"com": AIEngine.COM_TYPE_ASSERTZ,
					"data": fact["data"],
				})

				i -= 1

			else:
				i += 1

		return r_history

	def init(self, history):

		self._init_prolog()

		for fact in history:
			self.ack_fact(fact["com"], fact["data"])

	def _init_prolog(self):

		if self.prolog is not None:
			#raise RuntimeError("Resetting Prolog is impossible")
			return

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
