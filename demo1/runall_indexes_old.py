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
	# -----------------------------------------------------------------------------
	# --
	# -- run single without cache
	# --
	delta = cfg.test1
	basespec = projectContainer(cfg.basespec,cfg.n100spec)
	cfg_acc_pairs = runBacktestsWithCache(basespec=basespec,delta=delta,cache=store)
	features = set( featuresFromContainer(delta) )
	summary = summary_extractor(
		cfg_acc_pairs=cfg_acc_pairs,
		cfg_extractor=feature_extractor(features),
		acc_extractor=account_profit_summary,
	)
	colnames = shortnames(*features)+['profit']
	summary = rename_columns(summary,colnames)
	pprint(summary)

def runBacktestsWithCache(*,basespec,delta,cache,loadCache=True):
	all_rtcfg = configuration(basespec=basespec,variations=delta).all_configurations()
	result = []
	for rtcfg in tqdm(all_rtcfg,leave=None,desc='rtcfg'):
		(account,d0,universe,simulator) = runBacktestWithCache(rtspec=rtcfg,cache=cache,loadCache=loadCache)
		result.append( (rtcfg,account) )
	return result

def runBacktestWithCache(*,rtspec,cache,loadCache=True):
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
