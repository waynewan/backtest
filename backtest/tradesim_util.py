from jackutil.containerutil import cfg_to_obj,extractValue
import pandas as pd
from .account import PositionState
from .account_util import to_dataframe

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

def_excl = ['entryalgo', 'exitalgo', 'universe', 'sysfilter', 'simulator']
def build_objects(rtcfg, built_obj_map, excl=def_excl):
	if(built_obj_map is None):
		built_obj_map = {}
	for name in rtcfg.keys():
		if(name not in excl):
			_ = cfg_to_obj(rtcfg,name,built_obj_map)
	return built_obj_map

def load_all_objs(built_obj_map):
	for key,obj in built_obj_map.items():
		if("load" not in dir(obj)):
			continue
		obj.load()

def build_simulator(rtcfg):
	built_obj_map = build_objects(rtcfg, {})
	entryalgo = cfg_to_obj(rtcfg,"entryalgo",built_obj_map)
	exitalgo = cfg_to_obj(rtcfg,"exitalgo",built_obj_map)
	sysfilter = cfg_to_obj(rtcfg,"sysfilter",built_obj_map)
	#link_all_objs(built_obj_map)
	# --
	pp_opt = build_postprocessor( *entryalgo.postprocessor(), *exitalgo.postprocessor())
	universe = cfg_to_obj(rtcfg,"universe",built_obj_map,pp=pp_opt)
	sim_build_instr = rtcfg["simulator"]
	simulator = sim_build_instr["cls"](
		opt=sim_build_instr["opt"],
		universe=universe,
		sysfilter=sysfilter,
		entryalgo=entryalgo,
		exitalgo=exitalgo,
	)
	load_all_objs(built_obj_map)
	return simulator

def account_profit_summary(account):
	df0 = account.to_dataframe()
	if(len(df0.index)==0):
		return [ 0.0, 0.0 ]
	profit = df0['profit'].sum()
	df0['maxprofit'] = df0['cumprofit'].cummax()
	df0['drwdwn'] = df0['cumprofit'] / df0['maxprofit'] - 1.0
	return [ 
		profit / account.init_cash(), 
		df0['maxprofit'].max(), 
		df0['drwdwn'].min(),
	]

def account_profit_summary2(account):
	allpositions = account.positions()
	closedpos = allpositions[PositionState.CLOSED]
	failedpos = allpositions[PositionState.FAILED]
	closed_df = to_dataframe(closedpos.values())
	failed_df = to_dataframe(failedpos.values())
	closedpos_lst = sorted(list(closedpos.values()))
	failedpos_lst = sorted(list(failedpos.values()))
	# --
	return { 
		"# closed trades": len(closedpos_lst),
		"# failed trades": len(failedpos_lst),
	}

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

def loadAccountsFromStore(*,basespec,delta,cache):
	all_rtcfg = cfg.cfg(basespec=basespec,variations=delta).expand_all()
	cfg_acc_pairs = []
	for rtcfg in tqdm(all_rtcfg,leave=None,desc='rtcfg'):
		account,_,_,_ = cache.load(rtcfg)
		cfg_acc_pairs.append( (rtcfg,account) )
	return cfg_acc_pairs

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

