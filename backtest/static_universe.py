from jackutil.microfunc import str_to_dt,inrange
from backtest.abc.universe_abc import universe_abc
from . import norgate_helper as ngu
import datetime

class StaticUniverse(universe_abc):
	def __init__(self,*,opt,pp):
		self.__symbols = opt['symbols']
		self.__startdate = opt['date_range'][0]
		self.__enddate   = opt['date_range'][1]
		self.__nominal_size = len(self.__symbols)
		# --
		self._universe_abc__d0 = self.__load_d0(pp)
		self._universe_abc__trade_dates = self._universe_abc__d0.index.to_numpy()

	def __load_d0(self,pp_opt):
		df = ngu.load_history_for_symbols(self.__symbols,pp_opt)
		df = df[inrange(df.index,ge=self.__startdate,le=self.__enddate)]
		return df

	def symbols_at(self,as_of_date,exact=True):
		assert as_of_date is not None
		on_date = self._universe_abc__d0.loc[self._universe_abc__d0.index==as_of_date]
		if(exact and len(on_date)==0):
			raise Exception("no date")
		symbols = on_date.stack(level=1).dropna(axis=1,how='all').columns.to_numpy()
		return symbols

	def symbols_btw(self,startdate=None,enddate=None):
		if(startdate is None):
			startdate = str_to_dt('1970-01-01')
		if(enddate is None):
			enddate = datetime.datetime.now().date()
		# --
		uni = self._universe_abc__d0
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

# -- rm -- 	# --
# -- rm -- 	# ?? useless code below ??
# -- rm -- 	# --
# -- rm -- 	@property
# -- rm -- 	def size(self):
# -- rm -- 		return self.__universe_size
# -- rm -- 
# -- rm -- 	@property
# -- rm -- 	def universe(self):
# -- rm -- 		return self.__universe
# -- rm -- 
# -- rm -- 	# --
# -- rm -- 	# --
# -- rm -- 	# --
# -- rm -- 	def __load(self):
# -- rm -- 		df = ngu.load_major_exch_membership(self.__symbols)
# -- rm -- 		self.__universe = df.dropna(axis=1,how='all')
# -- rm -- 		self.__universe_size = len( self.__symbols )
# -- rm -- 
# -- rm -- 	# --
# -- rm -- 	# -- interface
# -- rm -- 	# --
# -- rm -- 	def symbols_at_(self,as_of_date,exact=False):
# -- rm -- 		assert as_of_date is not None
# -- rm -- 		on_or_before = self.__universe.loc[self.__universe.index<=as_of_date]
# -- rm -- 		if(len(on_or_before)==0):
# -- rm -- 			raise Exception("no member on date")
# -- rm -- 		members = on_or_before.iloc[-1]
# -- rm -- 		if(exact and not members.name==as_of_date):
# -- rm -- 			raise Exception("no date")
# -- rm -- 		members = members[members==1]
# -- rm -- 		return members.index.to_numpy()
# -- rm -- 
# -- rm -- 	# --
# -- rm -- 	# -- interface
# -- rm -- 	# --
# -- rm -- 	def symbols_btw_(self,startdate=None,enddate=None):
# -- rm -- 		if(startdate is None):
# -- rm -- 			# startdate = __0_date_str__('1970-01-01')
# -- rm -- 			startdate = str_to_dt('1970-01-01')
# -- rm -- 		if(enddate is None):
# -- rm -- 			enddate = datetime.datetime.now().date()
# -- rm -- 		# --
# -- rm -- 		uni = self.__universe
# -- rm -- 		# uni = uni[__inrange__(uni.index,ge=startdate,le=enddate)]
# -- rm -- 		uni = uni[inrange(uni.index,ge=startdate,le=enddate)]
# -- rm -- 		return uni.columns.to_numpy()
# -- rm -- 
# -- rm -- 	# --
# -- rm -- 	# -- interface
# -- rm -- 	# --
# -- rm -- 	def trade_dates_btw_(self,startdate=None,enddate=None):
# -- rm -- 		if(startdate is None):
# -- rm -- 			# startdate = __0_date_str__('1970-01-01')
# -- rm -- 			startdate = str_to_dt('1970-01-01')
# -- rm -- 		if(enddate is None):
# -- rm -- 			enddate = datetime.datetime.now().date()
# -- rm -- 		# --
# -- rm -- 		uni = self.__universe
# -- rm -- 		# uni = uni[__inrange__(uni.index,ge=startdate,le=enddate)]
# -- rm -- 		uni = uni[inrange(uni.index,ge=startdate,le=enddate)]
# -- rm -- 		return list( uni.index )
# -- rm -- 
