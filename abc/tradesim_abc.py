import abc
import logging

class tradesim_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self):
		self.__logger = logging.getLogger(__name__)

	@abc.abstractmethod
	def runBacktest(self):
		pass

	@abc.abstractmethod
	def runDailyAction(self,days):
		pass
