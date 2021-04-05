import matplotlib.pyplot as plt
from backtest import tradesim_store
from backtest import tradesim_rotational
import pandas as pd
import numpy as np
import random
from jackutil.containerutil import cfg_to_obj,projectContainer,containerChecksum
from tqdm.auto import tqdm
import pprint

def main():
	# -----------------------------------------------------------------------------
	import demo1_cfg as cfg
	store = tradesim_store.TradesimStore("D:/jnb_out/stoploss_research_15_v02")
	# -----------------------------------------------------------------------------
	# --
	# -- run single without cache
	# --
	rtcfg = projectContainer(cfg.basespec,cfg.n100spec)
	pprint.pprint(rtcfg)
	# --
	(account,d0,univers,simulator) = runBacktest(rtcfg=rtcfg)
	print(containerChecksum(rtcfg))
	print(account_profit_summary(account))

def runBacktest(rtcfg):
	simulator = build_simulator(rtcfg)
	(account,d0,universe) = simulator.runBacktest()
	return (account,d0,universe,simulator)

def runBacktestWithCache(*,rtcfg,cache,loadCache=True):
	has = np.array( cache.has(rtcfg=rtcfg) )
	has = has[has !=None]
	if(has.all()):
		print('.', end="")
		if(loadCache):
			return cache.load(rtcfg=rtcfg)[0:3]+(None,)
		else:
			return (None,None,None,None)
	# --
	(account,d0,universe,simulator) = runBacktest(rtcfg=rtcfg)
	cache.store(rtcfg,account=account,d0=d0,universe=universe)
	return (account,d0,universe,simulator)

def runBacktestsWithCache(*,basespec,delta,cache,shuffle=False,loadCache=True):
	all_rtcfg = cfg.cfg(basespec=basespec,variations=delta).expand_all()
	if(shuffle):
		random.shuffle(all_rtcfg)
	for rtcfg in tqdm(all_rtcfg,leave=None,desc='rtcfg'):
		(account,d0,universe,simulator) = runBacktestWithCache(rtcfg=rtcfg,cache=cache,loadCache=loadCache)

def account_profit_summary(account):
	df = account.to_dataframe()
	if(len(df.index)==0):
		return [ 0.0 ]
	profit = df['profit'].sum()
	return [ profit / account.init_cash() ]

# --
# --
# --
def build_postprocessor(*pp_list):
	pps = []
	for pp in pp_list:
		if(pp in pps):
			continue
		pps.append(pp)
	return pps

def build_simulator(rtcfg):
	built_obj_map = {}
	entryalgo = cfg_to_obj(rtcfg,"entryalgo",built_obj_map)
	exitalgo = cfg_to_obj(rtcfg,"exitalgo",built_obj_map)
	pp_opt = build_postprocessor( *entryalgo.postprocessor(), *exitalgo.postprocessor())
	universe = cfg_to_obj(rtcfg,"universe",built_obj_map,pp=pp_opt)
	sysfilter = cfg_to_obj(rtcfg,"sysfilter",built_obj_map)
	sim_build_instr = rtcfg["simulator"]
	return sim_build_instr["cls"](
		opt=sim_build_instr["opt"],
		universe=universe,
		sysfilter=sysfilter,
		entryalgo=entryalgo,
		exitalgo=exitalgo,
	)

# --
# -- ========== trash =================
# --

print(__name__)
if(__name__=="__main__"):
	main()
