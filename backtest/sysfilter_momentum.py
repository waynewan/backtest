from backtest import norgate_helper as ngu
from backtest.abc import sysfilter_abc
import pandas as pd
# --
# --
# --
class sysfilter_momentum(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__load(**self.__opt)

	def __load(self,*,symbol,benchmark,period,window,offset,ptype,smooth):
		bm = ngu.load_ng_historical(benchmark)
		hist0 = ngu.load_ng_historical(symbol)
		hist0['r0'] = 100 * ( hist0['Close'] / hist0['Close'].shift(period) - 1)
		self._d0 = hist0
		# --
		if(ptype=="YIELD"):
			self._d0['r0'] = hist0['r0'] - bm['Close'] - offset
		elif(ptype=="CASH"):
			bm['r0'] = 100 * ( bm['Close'] / bm['Close'].shift(period) - 1)
			self._d0['r0'] = hist0['r0'] - bm['r0'] - offset
		# --
		if(smooth=='min'):
			self._d0['r0'] = self._d0['r0'].rolling(window).min()
		elif(smooth=='max'):
			self._d0['r0'] = self._d0['r0'].rolling(window).max()
		elif(smooth=='mean'):
			self._d0['r0'] = self._d0['r0'].rolling(window).mean()

	def allow_entry(self,dt):
		if(dt in self._d0.index):
			return self._d0.loc[dt,'r0'] > 0.0
		return False

	def allow_exit(self,dt):
		return True

	def current_market_condition(self,dt):
		return {}

	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)

