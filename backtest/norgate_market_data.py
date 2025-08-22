# --
# --
# --
import norgatedata as ngd
# --
# --
# --
from jackutil.microfunc import make_callable,str_to_dt,inrange
from backtest.abc.market_data_abc import marketdata_abc
from tqdm.auto import tqdm
import pandas as pd
import functools
import json
import math

# --
# -- export utilities
# --
def export_index(ng=None,ngoff=None,short=None,name=None):
	mbr = ng.load_index_membership(name=name,short=short)
	ngoff.store_index_membersihp(mbr,name=name,short=short)
	return mbr

def export_indexes(ng=None,ngoff=None,shorts=None):
	symbols = set()
	for short in tqdm(shorts,desc='indexes'):
		mbr = export_index(ng=ng,ngoff=ngoff,short=short)
		symbols.update(mbr.columns)
	return symbols

def export_symbol(ng=None,ngoff=None,symbol=None):
	ohlc = _private_load_ng_historical(symbol)
	ngoff.store_symbol(ohlc,symbol)
	return ohlc

def export_symbols(ng=None,ngoff=None,symbols=None):
	for symbol in tqdm(symbols,leave=None,desc='export symbols'):
		_ = export_symbol(ng=ng,ngoff=ngoff,symbol=symbol)
		
def export_indexes_and_members(ng=None,ngoff=None,shorts=None):
	symbols_set = export_indexes(ng=ng,ngoff=ngoff,shorts=shorts)
	export_symbols(ng=ng,ngoff=ngoff,symbols=symbols_set)
	return symbols_set

# --
# --
# --
indexes = (
	( "name"        , "short", "benchmark", "count", "watchlist"                         ),
	( "Russell 1000", "r1000", "IWB",       1000,    "Russell 1000 Current & Past"       ),
	( "Russell 2000", "r2000", "IWM",       2000,    "Russell 2000 Current & Past"       ),
	( "Russell 3000", "r3000", "IWV",       3000,    "Russell 3000 Current & Past"       ),
	( "S&P 500"     , "s500",  "SPY",       500 ,    "S&P 500 Current & Past"            ),
	( "S&P 400"     , "s400",  "IJH",       400 ,    "S&P MidCap 400 Current & Past"     ),
	( "S&P 600"     , "s600",  "IJR",       600 ,    "S&P SmallCap 600 Current & Past"   ),
	( "S&P 1500"    , "s1500", "IWV",       1500,    "S&P Composite 1500 Current & Past" ),
	( "NASDAQ 100"  , "n100",  "QQQ",       100 ,    "Nasdaq 100 Current & Past"         ),
	( "economic"    , "econ",  "DIA",         0 ,    "economic"                          ),
	( "benchmark"   , "bmrk",  "DIA",         0 ,    "benchmark ETFs"                    ),
)
indexes_df = pd.DataFrame(indexes[1:], columns=indexes[0])
all_index_shorts = indexes_df[indexes_df['count']>0]['short'].tolist()
# --
# --
# --
def _private_watchlist_for(name=None,short=None):
	if(name is not None):
		index = indexes_df[indexes_df['name']==name]
		return index.iloc[0]['watchlist']
	elif(short is not None):
		index = indexes_df[indexes_df['short']==short]
		return index.iloc[0]['watchlist']
	raise ValueError("missing name/short")

# --
# --
# --
@functools.lru_cache(maxsize=20)
def _private_load_ng_index_membership(watchlist,symbol,startdate=str_to_dt('1970-01-01'),enddate=None):
	mbr_array = ngd.index_constituent_timeseries(
		symbol,
		watchlist,
		start_date=startdate,
		end_date=enddate,
		padding_setting=ngd.PaddingType.ALLWEEKDAYS,
		format='pandas-dataframe')
	mbr_array.rename(inplace=True,columns={"Index Constituent":symbol})
	mbr_array.replace(0,math.nan,inplace=True)
	return mbr_array

@functools.lru_cache(maxsize=20)
def _private_load_index_membership_impl(watchlist,symbols=None):
	mbr_arrays = []
	symbar = tqdm(symbols,leave=None,desc=f'"{watchlist}" members')
	for symbol in symbar:
		mbr_array = _private_load_ng_index_membership(watchlist,symbol)
		mbr_arrays.append(mbr_array) 
	mbr_df = pd.concat(mbr_arrays,axis=1)
	return mbr_df

def economic_data_series(symbol):
	if(symbol.startswith('%')):
		return True

@functools.lru_cache(maxsize=12000)
def _private_load_history_impl(symbol,pp_opt=None,startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
	ngprice = _private_load_ng_historical(symbol,startdate=startdate,enddate=enddate,interval=interval).copy()
	if(economic_data_series(symbol)):
		return ngprice
	# --
	if(len(ngprice)==0):
		# --
		# -- no data in range
		# --
		return None
	# --
	ngprice.drop(inplace=True,columns=['Turnover','Dividend'])
	ngprice.rename(inplace=True,columns={ 'Unadjusted Close':'Uclose' })
	ngprice['note'] = ""
	ngprice['last_n_bar'] = range(len(ngprice)-1,-1,-1)
	ngprice['n_bar'] = range(0,len(ngprice),1)
	# --
	for pp in _private_postprocessors(pp_opt) :
		pp(symbol,ngprice)
	return ngprice

def _private_load_ng_historical(symbol,startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
	pricedata = ngd.price_timeseries(
		symbol,
		stock_price_adjustment_setting = ngd.StockPriceAdjustmentType.TOTALRETURN,
		padding_setting=ngd.PaddingType.ALLWEEKDAYS,
		start_date = startdate,
		end_date = enddate,
		interval=interval,
		format='pandas-dataframe'
	)
	return pricedata

@functools.lru_cache(maxsize=12000)
def _private_postprocessors(pp_opt):
	# !!
	# !! does not provide default, let it fail, !!
	# !! so user know something is missing	    !!
	# !!
	pp_opt = json.loads(pp_opt)
	pp_list = []
	for funcspec,fopt in pp_opt:
		if(not callable(funcspec)):
			funcspec = make_callable(funcspec)
		pp_list.append(functools.partial(funcspec, **fopt))
	return pp_list

def clear_all_lru_caches():
	import sys
	module = sys.modules[__name__]
	for item_name in dir(module):
		item = getattr(module, item_name)
		if callable(item) and hasattr(item, 'cache_clear'):
			item.cache_clear()
			print(f"Cleared cache for: {item_name}")

def display_all_update_time():
	for db in ngd.databases():
		print(db, ngd.last_database_update_time(db))

# --
# --
# --
class Norgate(marketdata_abc):
	def __init__(self,*,opt=None):
		super().__init__()
		# _clear_all_lru_caches()
		display_all_update_time()
	# --
	# --
	# --
	def member_count_for(self,name=None,short=None):
		if(name is not None):
			index = indexes_df[indexes_df['name']==name]
			return index.iloc[0]['count']
		elif(short is not None):
			index = indexes_df[indexes_df['short']==short]
			return index.iloc[0]['count']
		raise ValueError("missing name/short")

	# --
	# -- return table, (col:symbol, row:date)==1 if symbol is index member at date
	# --
	def load_index_membership(self,name=None,short=None,symbols=None):
		watchlist = _private_watchlist_for(name=name,short=short)
		if(symbols is None):
			symbols = self.load_index_universe(name=name,short=short)
		return _private_load_index_membership_impl(watchlist, tuple(symbols))

	# --
	# -- return symbols list of index, current and past
	# --
	def load_index_universe(self,name=None,short=None):
		watchlist = _private_watchlist_for(name=name,short=short)
		symbols = ngd.watchlist_symbols(watchlist)
		return symbols

	# --
	# -- return symbols list of watchlist
	# --
	def load_watchlist_symbols(self,watchlist=None):
		symbols = ngd.watchlist_symbols(watchlist)
		return symbols

	def load_history_for_symbol(self,symbol,pp_opt={},startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
		data = self.load_history_for_symbols([symbol],pp_opt=pp_opt,startdate=startdate,enddate=enddate,interval=interval)
		return data[symbol]

	def load_history_for_symbols(self,symbols,pp_opt={},startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
		pp_opt_json = json.dumps(pp_opt)
		pricehistory = {}
		symbar = tqdm(symbols,leave=None,desc="history")
		for symbol in symbar:
			df = _private_load_history_impl(
				symbol,
				pp_opt=pp_opt_json,
				startdate=startdate,
				enddate=enddate,
				interval=interval
			)
			if(df is not None):
				pricehistory[symbol] = df
		pricehistory = pd.concat(pricehistory.values(),keys=pricehistory.keys(),axis=1)
		return pricehistory

