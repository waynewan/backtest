from backtest.abc.exitalgo_abc import exitalgo_abc

# --
# --
# --
class exitalgo_sysfilter(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__sysfilter = self.__opt.get('sysfilter','sysfilter')

	def link(self,linker):
		self.__sysfilter = linker(self.__sysfilter)

	# --
	# --
	# --
	def _read_sysfilter(self): return self.__sysfilter
	sysfilter = property(_read_sysfilter,None,None)
	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)
	# --
	# --
	# --
	def postprocessor(self):
		return []

	# --
	# -- return reason string if exit triggered
	# -- otherwise, return None
	# --
	def check_stopout_cond(self,dt,pos,bar):
		if(pos.exit_conditions['not_allow_entry'].value==True):
			return "failed_sysfilter"
		return None

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		return {
			"not_allow_entry" : {
				'upd_date' : dt,
				'upd_msg' : None,
				'new_val' : not self.__sysfilter.allow_entry(dt),
			},
		}
