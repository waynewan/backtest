# from common import __0_date_str__,__inrange__
from jackutil.microfunc import str_to_dt,inrange
import datetime
import norgate_helper as ngu

class ListUniverse:
	def __init__(self,symbols):
		self.__symbols = symbols
		self.__universe = None
		self.__universe_size = None
		self.__load()

	@property
	def size(self):
		return self.__universe_size

	@property
	def universe(self):
		return self.__universe

	# --
	# --
	# --
	def __load(self):
		df = ngu.load_major_exch_membership(self.__symbols)
		self.__universe = df.dropna(axis=1,how='all')
		self.__universe_size = len( self.__symbols )

# -- 	def inconsistent_symbol_count(self,count,threshold):
# -- 		inconsistent = abs(1-count/self.__universe_size)>threshold
# -- 		return inconsistent

	# --
	# -- interface
	# --
	def symbols_at_(self,as_of_date,exact=False):
		assert as_of_date is not None
		on_or_before = self.__universe.loc[self.__universe.index<=as_of_date]
		if(len(on_or_before)==0):
			raise Exception("no member on date")
		members = on_or_before.iloc[-1]
		if(exact and not members.name==as_of_date):
			raise Exception("no date")
		members = members[members==1]
		return members.index.to_numpy()

	# --
	# -- interface
	# --
	def symbols_btw_(self,startdate=None,enddate=None):
		if(startdate is None):
			# startdate = __0_date_str__('1970-01-01')
			startdate = str_to_dt('1970-01-01')
		if(enddate is None):
			enddate = datetime.datetime.now().date()
		# --
		uni = self.__universe
		# uni = uni[__inrange__(uni.index,ge=startdate,le=enddate)]
		uni = uni[inrange(uni.index,ge=startdate,le=enddate)]
		return uni.columns.to_numpy()

	# --
	# -- interface
	# --
	def trade_dates_btw_(self,startdate=None,enddate=None):
		if(startdate is None):
			# startdate = __0_date_str__('1970-01-01')
			startdate = str_to_dt('1970-01-01')
		if(enddate is None):
			enddate = datetime.datetime.now().date()
		# --
		uni = self.__universe
		# uni = uni[__inrange__(uni.index,ge=startdate,le=enddate)]
		uni = uni[inrange(uni.index,ge=startdate,le=enddate)]
		return list( uni.index )

