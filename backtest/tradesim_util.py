from jackutil.containerutil import cfg_to_obj,extractValue
import pandas as pd

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

def account_profit_summary(account):
	df = account.to_dataframe()
	if(len(df.index)==0):
		return [ 0.0 ]
	profit = df['profit'].sum()
	return [ profit / account.init_cash() ]

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

