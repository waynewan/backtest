from jackutil.microfunc import callable_fq_name
from backtest.abc.exitalgo_abc import exitalgo_abc
from backtest import norgate_helper
import pandas as pd
import numpy as np

# --
# -- "targets" : [ (25,0),(50,25),(100,50),(200,150) ]
# -- when price reach 125%, stop set to 100% of entry price
# -- stops only ratchet up
# --
class exitalgo_step_targets(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__table = list( zip(opt['targets'], opt['targets'][1:]) )
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
		if(pos.exit_conditions['step_target_price'].value>=bar['Close']):
			return "target_price_reach"
		return None

	# --
	# -- if "targets" is [ (-1, -35),(25,0),(50,25),(100,50),(200,150) ]
	# -- __table is [ 
	# -- 	[ (-100,-35),  ( 25,  0) ],
	# -- 	[ (  25,  0),  ( 50, 25) ],
	# -- 	[ (  50, 25),  (100, 50) ],
	# -- 	[ ( 100, 50),  (200,150) ],
	# -- ]
	# --
	def compute_stop_price(self,bar,entry_price):
		gain = 100.00 * ( bar['Close'] / entry_price ) - 100.00
		for lhs,rhs in self.__table:
			if(lhs[0] < gain <= rhs[0]):
				return entry_price + entry_price * lhs[1] / 100.00 
		return entry_price + entry_price * self.__table[-1][1][1] / 100.00 
		
	def calc_all_exit_conditions(self,dt,bar,*,entry_exec_date,entry_price):
		return {
			"step_target_price" : {
				'upd_date' : dt,
				'upd_msg' : None,
				'new_val' : self.compute_stop_price(bar,entry_price),
			},
		}

