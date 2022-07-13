from jackutil.microfunc import callable_fq_name
from backtest.abc.exitalgo_abc import exitalgo_abc
from backtest import norgate_helper
import pandas as pd
import numpy as np

# --
# --
# --
class exitalgo_target_price(exitalgo_abc):
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
	def check_stopout_cond(self,dt,pos,bar,bars):
		if(bar['Close']>=pos.exit_conditions['target_price'].value):
			return "target_price_reach"
		return None

	def calc_all_exit_conditions(self,dt,bar,*,entry_exec_date,entry_price):
		return {
			"target_price" : {
				'upd_date' : dt,
				'upd_msg' : None,
				'new_val' : entry_price * ( 1 + self.__opt["target_price_pct"] ),
			},
		}

