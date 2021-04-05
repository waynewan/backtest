from jackutil.containerutil import containerChecksum
from jackutil.configuration import configuration
from tqdm.auto import tqdm
from backtest import tradesim_store
from backtest.tradesim_util import build_simulator,account_profit_summary
import pandas as pd
import numpy as np
import pprint

def main():
	# -----------------------------------------------------------------------------
	import demo1_cfg as cfg
	store = tradesim_store.TradesimStore(".")
	# -----------------------------------------------------------------------------
	# --
	# -- run single without cache
	# --
	result = runBacktestsWithCache(basespec=cfg.basespec,delta=cfg.index_specific_setup,cache=store)
	pprint.pprint(result)

def runBacktestsWithCache(*,basespec,delta,cache,loadCache=True):
	all_rtcfg = configuration(basespec=basespec,variations=delta).all_configurations()
	result = {}
	for rtcfg in tqdm(all_rtcfg,leave=None,desc='rtcfg'):
		(account,d0,universe,simulator) = runBacktestWithCache(rtspec=rtcfg,cache=cache,loadCache=loadCache)
		result[containerChecksum(rtcfg)] = account_profit_summary(account)
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
