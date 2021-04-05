import abc

class exitalgo_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self):
		pass

	@abc.abstractmethod
	def postprocessor(self):
		pass

	# --
	# -- return reason string if exit triggered
	# -- otherwise, return None
	# --
	@abc.abstractmethod
	def check_stopout_cond(self,dt,pos,bar):
		pass

	@abc.abstractmethod
	def update_trailing_stop_for(self,dt,pos,bar):
		pass


