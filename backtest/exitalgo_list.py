from jackutil.containerutil import cfg_to_obj
from backtest.abc.exitalgo_abc import exitalgo_abc

# --
# --
# --
class exitalgo_list(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__keys = [ x for x in self.__opt['objs'] if(not x.startswith("__")) ]
		self.__algos = { key:None for key in set(self.__keys) }

	def link(self,linker):
		for key in self.__algos.keys():
			self.__algos[key] = linker(key)
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
	def check_stopout_cond(self,dt,pos,bar):
		for key,algo in self.__algos.items():
			result = algo.check_stopout_cond(dt,pos,bar)
			if(result is not None):
				return "/".join([key,result])
		return None

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		# --
		# !! pos.exit_conditions is a "defaultdict"
		# !! does not need store extra information
		# --
		for akey,algo in self.__algos.items():
			algo.calc_all_exit_conditions(dt,pos,bar,bars,universe)

