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
from backtest.abc.exitalgo_abc import *
import pandas as pd
import numpy as np
import scipy.stats as stats
import random

class exitalgo_rnddays(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__last_dt = None
		self.__opt = opt
		if('seed' in opt):
			if(opt['seed'] is not None):
				np.random.seed(opt['seed'])
		self.__min_days = self.__opt["min_days"]
		self.__max_days = self.__opt["max_days"]
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
		if(dt>=pos.exit_conditions['target_exit_date'].value):
			return "target_exit_date_reached"
		return None

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		# --
		# -- only update once
		# --
		cond_name = "target_exit_date"
		curval = pos.exit_conditions[cond_name]
		if(curval.hasvalue()):
			return
		curval.value = (pos.entry_exec_date + np.timedelta64(random.randint(self.__min_days,self.__max_days),'D'),dt,None)

