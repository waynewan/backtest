from jackutil.containerutil import cfg_to_obj

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


