from jackutil.microfunc import make_callable,str_to_dt
from tqdm.auto import tqdm
import pandas as pd
import math
import functools
import json
import norgatedata as ng

# --
# -- must run on norgate data update machine
# --

# --
# -- index _constituent
# --
_g_index_database_ = {
	"Russell 1000" : ( "Russell 1000 Current & Past", "IWB", 1000 ),
	"Russell 2000" : ( "Russell 2000 Current & Past", "IWM", 2000 ),
	"Russell 3000" : ( "Russell 3000 Current & Past", "IWV", 3000 ),
	"S&P 500" : ( "S&P 500 Current & Past", "SPY", 500 ),
	"S&P 400" : ( "S&P MidCap 400 Current & Past", "IJH", 400 ),
	"S&P 600" : ( "S&P SmallCap 600 Current & Past", "IJR", 600 ),
	"S&P 1500" : ( "S&P Composite 1500 Current & Past", "IWV", 1500 ),
	"NASDAQ 100" : ( "NASDAQ 100 Current & Past", "QQQ", 100 ),
	"NASDAQ 50" : ( "NASDAQ Q-50 Current & Past", "QQQ", 50 ),
}
# --
# -- index membership loaders
# --
def watchlist_for(indexname):
	return _g_index_database_[indexname][0]

def benchmark_for(indexname):
	return _g_index_database_[indexname][1]

def member_count_for(indexname):
	return _g_index_database_[indexname][2]

@functools.lru_cache(maxsize=8000)
def load_index_universe(indexname):
	watchlist = watchlist_for(indexname)
	symbols = ng.watchlist_symbols(watchlist)
	return symbols

@functools.lru_cache(maxsize=8000)
def load_ng_index_membership(indexname,symbol,startdate=str_to_dt('1970-01-01'),enddate=None):
	mbr_array = ng.index_constituent_timeseries(
		symbol,
		indexname,
		start_date=startdate,
		end_date=enddate,
		padding_setting=ng.PaddingType.ALLWEEKDAYS,
		format='pandas-dataframe')
	mbr_array.rename(inplace=True,columns={"Index Constituent":symbol})
	mbr_array.replace(0,math.nan,inplace=True)
	return mbr_array

@functools.lru_cache(maxsize=8000)
def load_index_membership_impl(indexname,symbols):
	mbr_arrays = []
	symbar = tqdm(symbols,leave=None,desc="index")
	for symbol in symbar:
		mbr_array = load_ng_index_membership(indexname,symbol)
		mbr_arrays.append(mbr_array) 
	mbr_df = pd.concat(mbr_arrays,axis=1)
	return mbr_df

def load_index_membership(indexname,symbols=None):
	if(symbols is None):
		symbols = load_index_universe(indexname)
	return load_index_membership_impl(indexname, tuple(symbols))

def members(memberships,as_of_date,indexname=None,threshold=None,exact=True):
	on_or_before = memberships.loc[memberships.index<=as_of_date]
	if(len(on_or_before)==0):
		raise Exception("no member on date")
	members = on_or_before.iloc[-1]
	if(exact and not members.name==as_of_date):
		raise Exception("no date")
	# --
	if(indexname is None):
		target_threshold = 0.1
		last_members_count = members.sum()
		inconsistent_symbol_count = abs(1 - last_members_count/member_count_for(indexname))>target_threshold
		if(inconsistent_symbol_count):
			raise Exception("inconsistent_symbol_count_against_target")
	# --
	if(threshold is not None and not math.isnan(threshold)):
		recent_members_count = on_or_before.iloc[-10:-2].sum(axis=1).mean()
		inconsistent_symbol_count = abs(1 - last_members_count/recent_members_count)>threshold
		if(inconsistent_symbol_count):
			raise Exception("inconsistent_symbol_count")
	members = members[members==1]
	return members.name,members.index.to_numpy()

# --
# -- major exch traded
# --
@functools.lru_cache(maxsize=8000)
def load_ng_major_exch_listed(symbol):
	majexch = ng.major_exchange_listed_timeseries(
		symbol,
		padding_setting=ng.PaddingType.ALLWEEKDAYS,
		format='pandas-dataframe')
	majexch.rename(inplace=True,columns={"Major Exchange Listed":symbol})
	majexch.replace(0,math.nan,inplace=True)
	return majexch

def load_major_exch_membership(symbols):
	mbr_arrays = []
	symbar = tqdm(symbols,leave=None,desc="exch listing")
	for sym in symbar:
		mbr_array = load_ng_major_exch_listed(sym)
		mbr_arrays.append(mbr_array) 
	mbr_df = pd.concat(mbr_arrays,axis=1)
	return mbr_df

# --
# -- price series
# --
@functools.lru_cache(maxsize=8000)
def postprocessors(pp_opt):
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

def load_ng_historical(symbol,startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
	pricedata = ng.price_timeseries(
		symbol,
		stock_price_adjustment_setting = ng.StockPriceAdjustmentType.TOTALRETURN,
		padding_setting=ng.PaddingType.ALLWEEKDAYS,
		start_date = startdate,
		end_date = enddate,
		interval=interval,
		format='pandas-dataframe'
	)
	return pricedata

@functools.lru_cache(maxsize=8000)
def load_history(symbol,pp_opt=None,startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
	ngprice = load_ng_historical(symbol,startdate=startdate,enddate=enddate,interval=interval).copy()
	# --
	ngprice.drop(inplace=True,columns=['Turnover','Dividend'])
	ngprice.rename(inplace=True,columns={ 'Unadjusted Close':'Uclose' })
	ngprice['note'] = ""
	ngprice['last_n_bar'] = range(len(ngprice)-1,-1,-1)
	# --
	for pp in postprocessors(pp_opt) :
		pp(symbol,ngprice)
	return ngprice

def load_history_for_symbols(symbols,pp_opt={},startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
	pp_opt_json = json.dumps(pp_opt)
	pricehistory = {}
	symbar = tqdm(symbols,leave=None,desc="history")
	for symbol in symbar:
		pricehistory[symbol] = load_history(symbol,pp_opt=pp_opt_json,startdate=startdate,enddate=enddate,interval=interval)
	pricehistory = pd.concat(pricehistory.values(),keys=pricehistory.keys(),axis=1)
	return pricehistory

# --
# -- control
# --
def clear_cache():
	load_history.cache_clear()
	load_index_membership_impl.cache_clear()
	load_index_universe.cache_clear()
	load_ng_index_membership.cache_clear()
	load_ng_major_exch_listed.cache_clear()
	postprocessors.cache_clear()

# --
# -- default price series post processors
# --
def pp_ng_default(symbol,data,**kv):
	data.loc[data.index[-2:].values,"note"] = "LAST_BAR"
	data['mbr'] = 0
	for k,v in kv.items():
		data[k] = v
	return data

# --
# --
# --
def pp_ng_index_mbr(symbol,data,indexname):
	mbr_array = load_ng_index_membership(indexname,symbol)
	data['mbr'] = mbr_array
	return data

