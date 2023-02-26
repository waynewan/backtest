from backtest.abc import sysfilter_abc
from jackutil.microfunc import inrange
import pandas as pd
import numpy as np

# --
# --
# --
class sysfilter_schedule(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__dsrc = None

	def link(self,linker):
		self.__dsrc = linker(self.__opt.get("datasource","datasource"))

	def load(self):
		self.__load(**self.__opt)

	def __load(self,*,symbol,loader_fn=None,date_range=None,**kv):
		bm_hist = self.__dsrc.load_history_for_symbol(symbol)
		bm_hist = pd.Series(data=bm_hist.index)
		if(date_range is not None):
			bm_hist = bm_hist[inrange(bm_hist,ge=date_range[0], lt=date_range[1])]
		if(loader_fn is None):
			self._d0 = bm_hist
		elif(loader_fn=="default"):
			self._d0 = self.__def_load_fn(bm_hist,**kv)
		elif(type(loader_fn)=="function"):
			self._d0 = loader_fn(bm_hist,**kv)
		else:
			raise RuntimeError("unknown loader_fn:{}".format(loader_fn))

	# --
	# -- window is positive integer >= 1
	# --
	def __def_load_fn(self,bm_hist,window,width=1):
		rhs = bm_hist
		bm_hist = rhs.iloc[0:1]
		rhs = rhs.iloc[1:]
		while( len(rhs)>0 ):
			next_date = bm_hist.iloc[-1] + np.timedelta64(window,'D')
			lhs = rhs.loc[rhs<=next_date]
			rhs = rhs.loc[rhs>next_date]
			if(len(lhs)==0):
				lhs = rhs.iloc[0:1]
				rhs = rhs.iloc[1:]
			bm_hist = bm_hist.append(lhs.iloc[-width:])
		return bm_hist

	def allow_entry(self,dt):
		allow_entry_test = (dt in self._d0.tolist() )
		return allow_entry_test

	def allow_exit(self,dt):
		return True

	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)
