import abc

class sysfilter_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self):
		self._d0 = None

	@abc.abstractmethod
	def allow_entry(self,dt):
		pass

	@abc.abstractmethod
	def allow_exit(self,dt):
		pass

	def current_market_condition(self,dt):
		return {}

	# --
	# -- properties
	# --
	def _read_d0(self): return self._d0
	def _store_d0(self,val): self._d0 = val
	d0 = property(_read_d0,_store_d0,None)
