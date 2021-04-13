from jackutil.containerutil import containerChecksum,featuresFromContainer,projectContainer
from jackutil.configuration import configuration
from jackutil.microfunc import shortnames,rename_columns
from tqdm.auto import tqdm
from backtest import tradesim_store
from backtest.tradesim_util import build_simulator,account_profit_summary,summary_extractor,feature_extractor,runBacktestWithCache
import pandas as pd
import numpy as np
from pprint import pprint

def main():
	summary = runall()
	pprint(summary)

def runall():
	# -----------------------------------------------------------------------------
	import demo1_cfg as cfg
	# store = tradesim_store.TradesimStore("pickle_jar")
	store = None
	# -----------------------------------------------------------------------------
	# --
	# -- run single without cache
	# --
	delta = cfg.test1
	basespec = projectContainer(cfg.basespec,cfg.n100spec)
	summary = runBacktestsWithCache(basespec=basespec,delta=delta,cache=store)
	colnames = shortnames( *featuresFromContainer(delta))+['profit']
	summary = rename_columns(summary,colnames)
	summary = summary.sort_values(by='profit',ascending=False,na_position='last')
	return summary

def runBacktestsWithCache(*,basespec,delta,cache,loadCache=True):
	all_rtcfg = configuration(basespec=basespec,variations=delta)
	cfg_extractor = feature_extractor( featuresFromContainer(delta) )
	result = []
	for rtcfg in tqdm(all_rtcfg.all_configurations(),leave=None,desc='rtcfg'):
		(account,_,_,_) = runBacktestWithCache(rtspec=rtcfg,cache=cache,loadCache=loadCache)
		subresult = (
			*cfg_extractor(rtcfg),
			*account_profit_summary(account) 
		)
		result.append(subresult)
		del account
	return pd.DataFrame(result)

# --
# -- ======================================
# --

if(__name__=="__main__"):
	main()
