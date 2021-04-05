import abc

class entryalgo_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self):
		pass

	@abc.abstractmethod
	def postprocessor(self):
		pass

	@abc.abstractmethod
	def buy_list_on(self,dt,bars,universe):
		pass

