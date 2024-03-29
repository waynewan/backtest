from jackutil.microfunc import callable_fq_name,dt64_to_dt
from backtest.abc.exitalgo_abc import exitalgo_abc
from datetime import timedelta
import pandas as pd
import numpy as np

# --
# --
# --
class exitalgo_stop_loss(exitalgo_abc):
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
		if(bar['Close']<=pos.exit_conditions['stop_loss'].value):
			return "stop_loss_reach"
		return None

	def get_stoploss_anchor_price(self,pos,bar):
		if(self.__opt.get("trailing_stop_loss",True)):
			return bar['Close']
		else:
			return pos.entry_price

	def is_stoploss_effective(self,dt,pos):
		effective_after_days = self.__opt.get("effective_after",0)
		effective_after_date = pos.entry_exec_date + np.timedelta64(effective_after_days,'D')
		return dt >= effective_after_date

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		new_val = 0
		if(self.is_stoploss_effective(dt,pos)):
			new_val = ( 1 - self.__opt["stop_loss_pct"] / 100.00 ) * self.get_stoploss_anchor_price(pos,bar)
		self.update_pos_exit_condition_chandelier(
			pos, "stop_loss",
			new_val, dt, None
		)
