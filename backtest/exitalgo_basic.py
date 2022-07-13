from jackutil.microfunc import callable_fq_name
from backtest.abc.exitalgo_abc import exitalgo_abc
from backtest import norgate_helper
import pandas as pd
import numpy as np

# --
# --
# --
class exitalgo_basic(exitalgo_abc):
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
			[ callable_fq_name(norgate_helper.pp_ng_default),{} ],
		]
		return pp_opt

	# --
	# -- return reason string if exit triggered
	# -- otherwise, return None
	# --
	def check_stopout_cond(self,dt,pos,bar,bars,universe):
		if(bar['note']=='LAST_BAR'):
			return "end_of_listing"
		return None

	def calc_all_exit_conditions(self,dt,bar,*,entry_exec_date,entry_price):
		return {
		}

