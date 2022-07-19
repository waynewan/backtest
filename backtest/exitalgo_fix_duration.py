from jackutil.microfunc import callable_fq_name
from backtest.abc.exitalgo_abc import exitalgo_abc
from backtest import norgate_helper
import pandas as pd
import numpy as np

# --
# --
# --
class exitalgo_fix_duration(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)
	# --
	# --
	# --
	def postprocessor(self):
		pp_opt = [
		]
		return pp_opt

	# --
	# -- return reason string if exit triggered
	# -- otherwise, return None
	# --
	def check_stopout_cond(self,dt,pos,bar):
		if(dt>=pos.exit_conditions['duration_stop'].value):
			return "target_exit_date"
		return None

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		return {
			"duration_stop" : {
				'upd_date' : dt,
				'upd_msg' : None,
				'new_val' : pos.entry_exec_date + np.timedelta64(self.__opt["duration"],'D'),
			},
		}

