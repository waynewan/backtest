from backtest import norgate_helper as ngu
from backtest.abc import sysfilter_abc
import pandas as pd
import numpy as np

# --
# --
# --
class sysfilter_schedule(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__load(**self.__opt)

	def __load(self,*,symbol,duration=None,window=1):
		bm_hist = ngu.load_ng_historical(symbol)
		# --
		rhs = bm_hist
		bm_hist = rhs.iloc[0:1]
		rhs = rhs.iloc[1:]
		while( len(rhs)>0 ):
			next_date = bm_hist.iloc[-1].name + np.timedelta64(duration,'D')
			lhs = rhs.loc[rhs.index<=next_date]
			rhs = rhs.loc[rhs.index>next_date]
			bm_hist = bm_hist.append(lhs.iloc[-window:-1])
		self._d0 = bm_hist

	def allow_entry(self,dt):
		return (dt in self._d0.index)

	def allow_exit(self,dt):
		return True

	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)

