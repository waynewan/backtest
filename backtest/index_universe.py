from jackutil.microfunc import str_to_dt,inrange
from backtest.abc.universe_abc import universe_abc
from . import norgate_helper as ngu
import datetime
import pandas as pd

_cached_index_membership_ = {}
_cached_daily_symbols_ = {}

class IndexUniverse(universe_abc):
	def __init__(self,*,opt,pp):
		super().__init__()
		self.__indexname = opt['indexname']
		self.__startdate = opt['date_range'][0]
		self.__enddate   = opt['date_range'][1]
		self.__membership,self.__nominal_size = self.__load_membership_cached()
		# --
		self._universe_abc__trade_dates = self.__membership.index.to_numpy()
		self._universe_abc__d0 = self.__load_d0(pp)

	def __load_membership_cached(self):
		key = self.__indexname
		if(key not in _cached_index_membership_):
			_cached_index_membership_[key] = self.__load_membership()
		return _cached_index_membership_[key]

	def __load_membership(self):
		df = ngu.load_index_membership(self.__indexname)
		df = df[inrange(df.index,ge=self.__startdate,le=self.__enddate)]
		membership = df.dropna(axis=1,how='all')
		nominal_size = ngu.member_count_for(self.__indexname)
		return (membership,nominal_size)

	def __load_d0(self,pp_opt):
		symbols = self.__membership.columns.to_numpy()
		df = ngu.load_history_for_symbols(symbols,pp_opt)
		return df
	# --
	# --
	# --
	def _read_indexname(self): return self.__indexname
	indexname = property(_read_indexname,None,None)
	def _read_size(self): return self.__membership_size
	size = property(_read_size,None,None)
	# --
	# --
	# --
	def inconsistent_symbol_count(self,count,threshold):
		inconsistent = abs(1-count/self.__membership_size)>threshold
		return inconsistent

	def symbols_at_cached(self,as_of_date,exact=True):
		key = (self.__indexname,as_of_date)
		if(key not in _cached_daily_symbols_):
			_cached_daily_symbols_[key] = self.symbols_at(as_of_date,exact)
		return _cached_daily_symbols_[key]

	def symbols_at(self,as_of_date,exact=True):
		assert as_of_date is not None
		on_date = self.__membership.loc[self.__membership.index==as_of_date]
		if(exact and len(on_date)==0):
			raise Exception("no date")
		members = on_date.iloc[-1]
		members = members[members==1]
		return members.index.to_numpy()

	def symbols_btw(self,startdate=None,enddate=None):
		if(startdate is None):
			startdate = str_to_dt('1970-01-01')
		if(enddate is None):
			enddate = datetime.datetime.now().date()
		# --
		uni = self.__membership
		uni = uni[inrange(uni.index,ge=startdate,le=enddate)]
		return uni.columns.to_numpy()

	def bars_on(self,dt=None):
		if(dt is None): dt = self.__asof_date
		assert dt is not None
		return self._universe_abc__d0.loc[dt].unstack(level=-1)
