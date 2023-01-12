from jackutil.microfunc import make_callable,str_to_dt,inrange
from backtest.abc.market_data_abc import marketdata_abc
from tqdm.auto import tqdm
import pandas as pd
import functools
import json
import os

# --
# -- utilities
# --
def init_export_folder(target_folder=None,must_be_empty=True):
	if(target_folder==None and reader.g_ng_export_dir()==None):
		raise FileNotFoundError(f"ng_export dir is not set")
	if(target_folder==None):
		target_folder = reader.g_ng_export_dir()
	if(not(os.path.isdir(target_folder))):
		raise FileNotFoundError(f"{target_folder} is not a valid directory")
	if(must_be_empty and len(os.listdir(target_folder))>0):
		raise FileNotFoundError(f"{target_folder} is not empty")
	# --
	os.mkdir(f'{target_folder}/mbr')
	for cc in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ":
		os.mkdir(f'{target_folder}/{cc}')

# --
# --
# --
indexes = (
	( "name"        , "benchmark", "count", "short", "loc" ),
	( "Russell 1000", "IWB",       1000,    "r1000", "mbr/mbr_r1000.par" ),
	( "Russell 2000", "IWM",       2000,    "r2000", "mbr/mbr_r2000.par" ),
	( "Russell 3000", "IWV",       3000,    "r3000", "mbr/mbr_r3000.par" ),
	( "S&P 500"     , "SPY",       500 ,    "s500",  "mbr/mbr_s500.par"  ),
	( "S&P 400"     , "IJH",       400 ,    "s400",  "mbr/mbr_s400.par"  ),
	( "S&P 600"     , "IJR",       600 ,    "s600",  "mbr/mbr_s600.par"  ),
	( "S&P 1500"    , "IWV",       1500,    "s1500", "mbr/mbr_s1500.par" ),
	( "NASDAQ 100"  , "QQQ",       100 ,    "n100",  "mbr/mbr_n100.par"  ),
)
indexes_df = pd.DataFrame(indexes[1:], columns=indexes[0])
# --
# -- 
# --
def symbol_filename_for(name):
	subfolder = name[0].upper()
	return f'{subfolder}/{name}.par'

def index_filename_for(name=None,short=None):
	if(name is not None):
		index = indexes_df[indexes_df['name']==name]
		return index.iloc[0]['loc']
	elif(short is not None):
		index = indexes_df[indexes_df['short']==short]
		return index.iloc[0]['loc']
	raise ValueError("missing name/short")

# --
# --
# --
@functools.lru_cache(maxsize=10)
def _private_load_index_membership_impl(loc=None,name=None,short=None):
	filename = index_filename_for(name=name,short=short)
	d0 = pd.read_parquet(f'{loc}/{filename}')
	d0.index = pd.to_datetime(d0.index, format='%Y-%m-%d')
	return d0

def _private_load_historical_impl(symbol,loc=None,startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
	if(interval !='D'):
		raise NotImplementedError
	filename = symbol_filename_for(symbol)
	fullpath = f'{loc}/{filename}'
	d0 = pd.read_parquet(fullpath)
	d0.index = pd.to_datetime(d0.index, format='%Y-%m-%d')
	if(startdate is not None and enddate is not None):
		d0 = d0[inrange(d0.index,ge=startdate,le=enddate)]
	return d0

@functools.lru_cache(maxsize=12000)
def _private_load_history_impl(symbol,pp_opt=None,loc=None,startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
	ngprice = _private_load_historical_impl(symbol,loc=loc,startdate=startdate,enddate=enddate,interval=interval).copy()
	# --
	ngprice.drop(inplace=True,columns=['Turnover','Dividend'])
	ngprice.rename(inplace=True,columns={ 'Unadjusted Close':'Uclose' })
	ngprice['note'] = ""
	ngprice['last_n_bar'] = range(len(ngprice)-1,-1,-1)
	# --
	for pp in _private_postprocessors(pp_opt) :
		pp(symbol,ngprice)
	return ngprice

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

# --
# --
# --
class NorgateOffline(marketdata_abc):
	def __init__(self,loc):
		super().__init__()
		self.__loc = loc
	# --
	# --
	# --
	def _read_loc(self): return self.__loc
	loc = property(_read_loc,None,None)
	# --
	# -- abstractmethod impl
	# --
	def load_index_membership(self,name=None,short=None,symbols=None):
		full_mbr_matrix = _private_load_index_membership_impl(loc=self.__loc,name=name,short=short)
		if(symbols is None):
			return full_mbr_matrix
		return full_mbr_matrix[symbols]

	def load_index_universe(self,name=None,short=None):
		mbr_matrix = self.load_index_membership(name=name,short=short)
		return mbr_matrix.columns.tolist()

	def load_history_for_symbol(self,symbol,pp_opt={},startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
		pp_opt_json = json.dumps(pp_opt)
		return _private_load_history_impl(
			symbol,
			pp_opt=pp_opt_json,
			loc=self.__loc,
			startdate=startdate,
			enddate=enddate,
			interval=interval
		)

	def load_history_for_symbols(self,symbols,pp_opt={},startdate=str_to_dt('1970-01-01'),enddate=None,interval="D"):
		pp_opt_json = json.dumps(pp_opt)
		pricehistory = {}
		symbar = tqdm(symbols,leave=None,desc="history")
		for symbol in symbar:
			pricehistory[symbol] = _private_load_history_impl(
				symbol,
				pp_opt=pp_opt_json,
				loc=self.__loc,
				startdate=startdate,
				enddate=enddate,
				interval=interval
			)
		pricehistory = pd.concat(pricehistory.values(),keys=pricehistory.keys(),axis=1)
		return pricehistory

	# --
	# --
	# --
	def store_index_membersihp(self,df,name=None,short=None):
		filename = index_filename_for(name=name,short=short)
		fullpath = f'{self.__loc}/{filename}'
		df.to_parquet(fullpath)
		return fullpath
	
	def store_symbol(self,df,symbol):
		filename = symbol_filename_for(symbol)
		fullpath = f'{self.__loc}/{filename}'
		df.to_parquet(fullpath)
		return df

