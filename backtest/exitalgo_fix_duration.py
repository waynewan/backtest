from jackutil.microfunc import if_else
from backtest.abc.exitalgo_abc import exitalgo_abc
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
	__exit_cond_name = "duration_stop"
	def check_stopout_cond(self,dt,pos,bar):
		return self.check_stopout_for_cond(self.__exit_cond_name,dt,pos,bar)

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		duration_stop = pos.entry_exec_date + np.timedelta64(self.__opt["duration"],'D')
		duration_stop_triggered = if_else(dt>=duration_stop, "duration_stop", None)
		# --
		new_value = (duration_stop, duration_stop_triggered)
		curval = pos.exit_conditions[self.__exit_cond_name]
		curval.value = (new_value,dt,None)

