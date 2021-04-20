import abc

class tradesim_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def runBacktest(self):
		pass

	@abc.abstractmethod
	def runDailyBuylist(self,days):
		pass
