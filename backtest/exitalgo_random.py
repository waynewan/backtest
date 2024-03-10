# --
# --
# --
import sys
import math
sys.path.append("../../common/lib/trade_secret_algo")
import algo_codelet_talib0 as codelet
# --
# --
# --
from jackutil.microfunc import inrange,callable_fq_name
from backtest.abc.exitalgo_abc import exitalgo_abc
import pandas as pd
import numpy as np
import scipy.stats as stats
import random

class exitalgo_random(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__last_dt = None
		self.__opt = opt
		self.__threshold = opt['threshold']
		if('seed' in opt):
			if(opt['seed'] is not None):
				np.random.seed(opt['seed'])
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
	# --
	# --
	def check_stopout_cond(self,dt,pos,bar):
		exit_roll = random.random()
		if(self.__threshold > exit_roll):
			return "random_roll_exceed_threshold"
		return None

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		return {
			"exit_random" : {
				'upd_date' : dt,
				'upd_msg' : None,
				'new_val' : 0,
			},
		}
		

