import abc

class entryalgo_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self):
		pass

	@abc.abstractmethod
	def postprocessor(self):
		pass

	# -- return None if okay to exec open
	# -- otherwise, return reason message
	@abc.abstractmethod
	def exec_open_final_check(self,symbol,bar):
		pass

	@abc.abstractmethod
	def buy_list_on(self,dt,bars,universe):
		pass

