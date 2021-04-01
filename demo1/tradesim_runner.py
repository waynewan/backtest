# --
# -- manage multiple tradesim runs using variation of cfg
# --
import matplotlib.pyplot as plt
from backtest import tradesim_store
from backtest import tradesim
import pandas as pd
import numpy as np
import random
from jackutil.containerutil import extractValue,projectContainer,containerChecksum
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
def build_object(component_name,rtcfg,built_obj_map,**kv):
	build_instruction = rtcfg[component_name]
	if(component_name in built_obj_map):
		return built_obj_map[component_name]
	elif(isinstance(build_instruction,str)):
		obj = build_object(build_instruction,rtcfg,built_obj_map,**kv)
		built_obj_map[component_name] = obj
		return obj
	else:
		obj_cls = build_instruction["cls"]
		obj_opt = build_instruction["opt"]
		obj = obj_cls(opt=obj_opt,**kv)
		built_obj_map[component_name] = obj
		return obj
	
def build_postprocessor(*pp_list):
	pps = []
	for pp in pp_list:
		if(pp in pps):
			continue
		pps.append(pp)
	return pps

def build_simulator(rtcfg):
	built_obj_map = {}
	entryalgo = build_object("entryalgo",rtcfg,built_obj_map)
	exitalgo = build_object("exitalgo",rtcfg,built_obj_map)
	pp_opt = build_postprocessor( *entryalgo.postprocessor(), *exitalgo.postprocessor())
	universe = build_object("universe",rtcfg,built_obj_map,pp=pp_opt)
	sysfilter = build_object("sysfilter",rtcfg,built_obj_map)
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
