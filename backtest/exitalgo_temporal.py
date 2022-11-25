from jackutil.containerutil import cfg_to_obj
from backtest.abc.exitalgo_abc import exitalgo_abc
import numpy as np

# --
# --
# --
class exitalgo_temporal(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__algos = {}
		for key,spec in self.__opt.items():
			if(type(spec) !=type({})):
				continue
			self.__algos[key] = cfg_to_obj(opt,key,self.__algos)
	# --
	# --
	# --
	def _read_algos(self): return self.__algos
	algos = property(_read_algos,None,None)
	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)
	# --
	# --
	# --
	def postprocessor(self):
		pp_opt = []
		for algo in self.__algos.values():
			pp_opt = [ *pp_opt, *algo.postprocessor() ]
		return pp_opt

	# --
	# -- return reason string if exit triggered
	# -- otherwise, return None
	# --
	def ineffective_interval(self,dt,pos,bar):
		effective_before = True
		effective_after = True
		if(self.__opt.get("effective_before")):
			effective_before_days = self.__opt.get("effective_before",0)
			effective_before_date = pos.entry_exec_date + np.timedelta64(effective_before_days,'D')
			effective_before = dt < effective_before_date
		if(self.__opt.get("effective_after")):
			effective_after_days = self.__opt.get("effective_after",0)
			effective_after_date = pos.entry_exec_date + np.timedelta64(effective_after_days,'D')
			effective_after = dt >= effective_after_date
		return (effective_before and effective_after)

	def check_stopout_cond(self,dt,pos,bar):
		for key,algo in self.__algos.items():
			result = algo.check_stopout_cond(dt,pos,bar)
			if(result is not None):
				return "/".join([key,result])
		return None

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe,sysfilter):
		if(self.ineffective_interval(dt,pos,bar)):
			return {}
		# --
		allconds = {}
		for akey,algo in self.__algos.items():
			conds = algo.calc_all_exit_conditions(dt,pos,bar,bars,universe,sysfilter)
			allconds.update(conds)
		return allconds

