from backtest.abc import sysfilter_abc
import pandas as pd
import numpy as np
# --
# --
# --
class sysfilter_momentum(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt

	def link(self,linker):
		self.__dsrc = linker(self.__opt.get("datasource","datasource"))

	def load(self):
		self.__load(**self.__opt)

	def __load(self,*,symbol,benchmark,period,window,offset,ptype,smooth):
		compare_dir_adj = np.sign(period)
		period = abs(period)
		# --
		hist0 = self.__dsrc.load_history_for_symbol(symbol)
		hist0['r0'] = compare_dir_adj * 100 * ( hist0['Close'] / hist0['Close'].shift(period) - 1)
		self._d0 = hist0.copy()
		if(ptype=="PRICE"):
			self.__smooth_function(smooth,window)
			return
		# --
		bm = self.__dsrc.load_history_for_symbol(benchmark)
		if(ptype=="YIELD"):
			self._d0['r0'] = hist0['r0'] - bm['Close'] - offset
		elif(ptype=="CASH"):
			bm['r0'] = compare_dir_adj * 100 * ( bm['Close'] / bm['Close'].shift(period) - 1)
			self._d0['r0'] = hist0['r0'] - bm['r0'] - offset
		else:
			raise ValueError(f"unknown ptype:{ptype}")
		self.__smooth_function(smooth,window)
		return

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

