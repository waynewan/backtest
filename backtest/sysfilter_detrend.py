from backtest.abc import sysfilter_abc
import pandas as pd
# --
# --
# --
class sysfilter_detrend(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt

	def link(self,linker):
		self.__dsrc = linker(self.__opt.get("datasource","datasource"))

	def load(self):
		self.__load(**self.__opt)

	def __load(self,*,symbol,period,smooth,window):
		hist0 = self.__dsrc.load_history_for_symbol(symbol)
		self._d0 = hist0.copy()
		self._d0['r0'] = hist0['Close'] / hist0['Close'].rolling(period).mean() * 100 - 100
		self.__smooth_function(smooth,window)

	def __smooth_function(self,smooth,window):
		if(smooth=='min'):
			self._d0['r0'] = self._d0['r0'].rolling(window).min()
		elif(smooth=='max'):
			self._d0['r0'] = self._d0['r0'].rolling(window).max()
		elif(smooth=='mean'):
			self._d0['r0'] = self._d0['r0'].rolling(window).mean()

	def allow_entry(self,dt):
		if(dt in self._d0.index):
			return self._d0.loc[dt,'r0'] >= 0.0
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

