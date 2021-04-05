from backtest import norgate_helper as ngu
from backtest.abc import sysfilter_abc
import pandas as pd
# --
# --
# --
class demo1_sysfilter(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__load(**self.__opt)

	def __load(self,*,symbol,period,algo):
		if(algo=="ALGO_1"):
			bm_hist = ngu.load_ng_historical(symbol)
			bm_hist['r0'] = bm_hist['Low'] / bm_hist['High'].rolling(period).mean()
			bm_hist['s0'] = ( bm_hist['r0'] >= 1 )
			self._d0 = bm_hist

	def allow_entry(self,dt):
		if(dt in self._d0.index):
			return self._d0.loc[dt,'s0']
		return False

	def allow_exit(self,dt):
		return True

	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)

