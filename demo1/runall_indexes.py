from jackutil.containerutil import containerChecksum,featuresFromContainer,projectContainer
from jackutil.configuration import configuration
from jackutil.microfunc import shortnames,rename_columns
from tqdm.auto import tqdm
from backtest import tradesim_store
from backtest.tradesim_util import build_simulator,account_profit_summary,summary_extractor,feature_extractor
import pandas as pd
import numpy as np
from pprint import pprint

def main():
	# -----------------------------------------------------------------------------
	import demo1_cfg as cfg
	store = tradesim_store.TradesimStore("pickle_jar")
	store = None
	# -----------------------------------------------------------------------------
	# --
	# -- run single without cache
	# --
	delta = cfg.test1
	basespec = projectContainer(cfg.basespec,cfg.n100spec)
	summary = runBacktestsWithCache(basespec=basespec,delta=delta,cache=store)
	features = set( featuresFromContainer(delta) )
	colnames = shortnames(*features)+['profit']
	summary = rename_columns(summary,colnames)
	summary = summary.sort_values(by='profit',ascending=False,na_position='last')
	pprint(summary)

def runBacktestsWithCache(*,basespec,delta,cache,loadCache=True):
	all_rtcfg = configuration(basespec=basespec,variations=delta).all_configurations()
	features = set( featuresFromContainer(delta) )
	cfg_extractor=feature_extractor(features)
	result = []
	for rtcfg in tqdm(all_rtcfg,leave=None,desc='rtcfg'):
		(account,_,_,_) = runBacktestWithCache(rtspec=rtcfg,cache=cache,loadCache=loadCache)
		result.append((
			*cfg_extractor(rtcfg),
			*account_profit_summary(account) 
		))
		del account
	return pd.DataFrame(result)

def runBacktestWithCache(*,rtspec,cache,loadCache=True):
	if(cache is None):
		(account,d0,universe,simulator) = runBacktest(rtcfg=rtspec)
		return (account,d0,universe,simulator)
	# --
	has = np.array( cache.has(rtspec=rtspec) )
	has = has[has !=None]
	if(has.all()):
		print('.', end="")
		if(loadCache):
			return cache.load(rtspec=rtspec)[0:3]+(None,)
		else:
			return (None,None,None,None)
	# --
	(account,d0,universe,simulator) = runBacktest(rtcfg=rtspec)
	cache.store(rtspec,account=account,d0=d0,universe=universe)
	return (account,d0,universe,simulator)

def runBacktest(rtcfg):
	simulator = build_simulator(rtcfg)
	(account,d0,universe) = simulator.runBacktest()
	return (account,d0,universe,simulator)

# --
# -- ======================================
# --

print(__name__)
if(__name__=="__main__"):
	main()
