from backtest.abc import sysfilter_abc
import pandas as pd
# --
# --
# --
class sysfilter_dummy(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt

	def allow_entry(self,dt):
		return True

	def allow_exit(self,dt):
		return True

	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)

