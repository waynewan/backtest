import matplotlib.pyplot as plt
from backtest import tradesim_store
from backtest import tradesim
import pandas as pd
import numpy as np
import random
from jackutil.containerutil import extractValue,projectContainer,containerChecksum
from tqdm.auto import tqdm
import pprint
# --
# --
# --
def plot_account_cumprofit(account,title=None):
	df0 = account.to_dataframe()
	df0.plot(x='exit_date',y='cumprofit',logy=True,figsize=(12,8),title=title)

def plot_multilines_by_category(df,*,category,xcol,ycol):
	df0 = df.pivot(index=xcol,columns=category,values=ycol)
	df0.plot()

def plot_3d_surface(title=None,data=None,ax=None):
	# --
	# -- use pivot(index=summary.columns[0],columns=summary.columns[1],values=summary.columns[2])
	# -- for example:
	# -- max_age	 300	 400	 500	 600	 700	 800	 900
	# -- maxpos														 
	# -- 5		142.42  164.48  331.14  324.42  294.71  279.05  296.55
	# -- 15	   136.87  164.50  287.95  308.02  245.78  227.77  223.29
	# -- 25	   101.27  110.37  195.94  205.23  177.73  172.17  164.12
	# -- 35		65.60   84.68  148.45  149.78  130.96  124.81  118.92
	# -- 45		54.97   72.64  117.07  114.45   98.54   96.33   92.28
	# -- 
	X,Y = np.meshgrid(data.index,data.columns)
	Z = data.T.to_numpy()
	ax.plot_surface(X=X,Y=Y,Z=Z,cmap='gray',edgecolor='none',alpha=0.5)
	ax.contour(X=X,Y=Y,Z=Z,zdir='x',cmap='Reds',offset=0)
	ax.contour(X=X,Y=Y,Z=Z,zdir='y',cmap='Greens',offset=np.max(Y))
	ax.set_title(title)
	ax.set_xlabel(data.index.name)
	ax.set_ylabel(data.columns.name)

def create_pivots_by_category(data,*,index,columns,values,categoryColumns=None):
	if(categoryColumns is None):
		categoryColumns = list( data.columns ) 
		categoryColumns.pop(categoryColumns.index(index))
		categoryColumns.pop(categoryColumns.index(columns))
		categoryColumns.pop(categoryColumns.index(values))
	categories = data.loc[:,categoryColumns].drop_duplicates()
	cat_to_pivots = {}
	for ii in range(0,len(categories)):
		ii_category = categories.iloc[ii]
		df = (data.loc[:,categoryColumns]==ii_category).all(axis=1)
		df = data[df].loc[:,(index,columns,values)]
		df = df.pivot(index=index,columns=columns,values=values)
		cat_to_pivots[tuple(ii_category.tolist())] = df
	return cat_to_pivots

# --
# -- loading and formatting accounts
# --
def loadAccountsFromStore(*,basespec,delta,cache):
	all_rtcfg = cfg.cfg(basespec=basespec,variations=delta).expand_all()
	cfg_acc_pairs = []
	for rtcfg in tqdm(all_rtcfg,leave=None,desc='rtcfg'):
		account,_,_,_ = cache.load(rtcfg)
		cfg_acc_pairs.append( (rtcfg,account) )
	return cfg_acc_pairs

def summary_extractor(*,cfg_acc_pairs,cfg_extractor,acc_extractor):
	result = []
	for cfg,account in cfg_acc_pairs:
		result.append((
			*cfg_extractor(cfg),
			*acc_extractor(account)
		))
	return pd.DataFrame(result)

def feature_extractor(features):
	def fn(rtcfg):
		values = []
		for feature in features:
			values.append(extractValue(rtcfg,path=feature))
		return values
	return fn

