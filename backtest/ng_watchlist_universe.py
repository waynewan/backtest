from jackutil.microfunc import str_to_dt,inrange
from backtest.abc.universe_abc import universe_abc
import datetime
import pandas as pd

_cached_index_membership_ = {}
_cached_daily_symbols_ = {}

class NorgateWatchlistUniverse(universe_abc):
	def __init__(self,*,opt,pp):
		super().__init__()
		self.__watchlist = opt['watchlist']
		self.__sample_size = opt.get('sample_size',None)
		self.__startdate = opt['date_range'][0]
		self.__enddate   = opt['date_range'][1]
		self.__opt = opt
		self.__pp = pp
		self.__interval = self.__opt.get("interval", "D")
		self.__dsrc = None

	def link(self,linker):
		self.__dsrc = linker(self.__opt.get("datasource","datasource"))

	def load(self):
		self.__membership,self.__nominal_size = self.__load_symbols()
		self._universe_abc__d0 = self.__load_d0(self.__interval,self.__pp)
		# --
		# -- some symbols in watchlist might be outside requested date range
		# --
		self.__membership = self._universe_abc__d0.columns.get_level_values(0).unique()
		self.__nominal_size = len(self.__membership)
		self._universe_abc__trade_dates = self._universe_abc__d0.index.to_numpy()

	def __load_symbols(self):
		symbols = self.__dsrc.load_watchlist_symbols(watchlist=self.__watchlist)
		if(self.__sample_size is not None):
			symbols = symbols[0:self.__sample_size]
		nominal_size = len(symbols)
		return (symbols,nominal_size)

	def __load_d0(self,interval,pp_opt):
		symbols = self.__membership
		df = self.__dsrc.load_history_for_symbols(symbols,pp_opt,startdate=self.__startdate,enddate=self.__enddate,interval=self.__interval)
		df = df[inrange(df.index,ge=self.__startdate,le=self.__enddate)]
		return df
	# --
	# --
	# --
	def _read_watchlist(self): return self.__watchlist
	watchlist = property(_read_watchlist,None,None)
	def _read_size(self): return self.__membership_size
	size = property(_read_size,None,None)
	# --
	# --
	# --
	def symbols_at_cached(self,as_of_date,exact=True):
		key = (self.__watchlist,as_of_date)
		if(key not in _cached_daily_symbols_):
			_cached_daily_symbols_[key] = self.symbols_at(as_of_date,exact)
		return _cached_daily_symbols_[key]

	def symbols_at(self,as_of_date,exact=True):
		return self.__membership
# --
#		on_date = self.__membership.loc[self.__membership.index==as_of_date]
#		if(exact and len(on_date)==0):
#			raise Exception("no date")
#		members = on_date.iloc[-1]
#		members = members[members==1]
#		return members.index.to_numpy()
# --

	def symbols_btw(self,startdate=None,enddate=None):
		if(startdate is None):
			startdate = str_to_dt('1970-01-01')
		if(enddate is None):
			enddate = datetime.datetime.now().date()
		# --
		uni = self.__membership
		uni = uni[inrange(uni.index,ge=startdate,le=enddate)]
		return uni.columns.to_numpy()

	def bars_on(self,dt=None,mbr_only=False):
		if(dt is None): dt = self.__asof_date
		assert dt is not None
		bars_on_dt = self._universe_abc__d0.loc[dt].unstack(level=-1)
		if(mbr_only):
			mbr_symbols = self.symbols_at(dt)
			bars_on_dt = bars_on_dt.loc[mbr_symbols]
		return bars_on_dt

