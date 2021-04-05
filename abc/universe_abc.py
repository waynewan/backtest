import abc

class universe_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self):
		self.__asof_date = None
		self.__trade_dates = None
		self.__d0 = None

	# --
	# -- read/write properties
	# --
	def _read_asof_date(self): return self.__asof_date
	def _store_asof_date(self,val):
		assert val is not None
		assert val in self.__trade_dates
		self.__asof_date = val
	asof_date = property(_read_asof_date,_store_asof_date,None)
	# --
	# -- read only properties
	# --
	def _read_d0(self): return self.__d0
	d0 = property(_read_d0,None,None)
	def _read_trade_dates(self): return self.__trade_dates
	trade_dates = property(_read_trade_dates,None,None)
	def _read_first_trade_date(self): return self.__trade_dates[0]
	first_trade_date = property(_read_first_trade_date,None,None)
	def _read_last_trade_date(self): return self.__trade_dates[-1]
	last_trade_date = property(_read_last_trade_date,None,None)
	# --
	# -- property queries
	# --
	def is_last_trade_date(self,dt=None):
		if(dt is None): dt = self.__asof_date
		assert dt is not None
		assert self.__asof_date is not None
		assert self.last_trade_date is not None
		return self.__asof_date==self.last_trade_date
	# --
	# -- abstract methods
	# --
	@abc.abstractmethod
	def bars_on(self,dt=None):
		pass
	@abc.abstractmethod
	def symbols_at(self,as_of_date,exact=False):
		pass
	@abc.abstractmethod
	def symbols_btw(self,startdate=None,enddate=None):
		pass
