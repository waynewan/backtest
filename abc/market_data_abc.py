import abc

class marketdata_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self):
		pass

	@abc.abstractmethod
	def member_count_for(self,name,short):
		pass

	@abc.abstractmethod
	def load_index_universe(self,name,short):
		pass

	@abc.abstractmethod
	def load_index_membership(indexname,symbols):
		pass

	@abc.abstractmethod
	def load_history_for_symbol(self,symbol,pp_opt,startdate,enddate,interval):
		pass

	@abc.abstractmethod
	def load_history_for_symbols(symbols,pp_opt,startdate,enddate,interval):
		pass

