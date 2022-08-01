from jackutil.containerutil import cfg_to_obj
from jackutil.microfunc import inrange,callable_fq_name,concat_lists
from backtest.abc.entryalgo_abc import entryalgo_abc
from backtest import norgate_helper
import pandas as pd
import numpy as np
import talib as ta
import scipy.stats as stats
import itertools as itt

# --
# --
# --
class entryalgo_collab(entryalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__algos = {}
		for key,spec in self.__opt.items():
			self.__algos[key] = cfg_to_obj(opt,key,self.__algos)
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

	def exec_open_final_check(self,symbol,bar):
		for key,algo in self.__algos.items():
			msg = algo.exec_open_final_check(symbol,bar)
			if(msg is not None):
				return msg
		return None

	# --
	# 1,3,5,2,4,6 -- R1k=35x,S500=65x,N100=116x
	# 1,2,3,4,5,6 -- R1k=65x,S500=55x,N100=123x
	# !! the first sequence makes more sense, 
	# !! because it eliminates all unwanted symbols first
	# !! the poor performance of R1k is a flute, if mapos +/-1
	# --
	def buy_list_on(self,dt,bars,universe):
		all_signals = []
		all_buylist = []
		for key,algo in self.__algos.items():
			(signals, buylist) = algo.buy_list_on(dt,bars,universe)
			all_buylist = concat_lists(all_buylist, buylist)
			all_signals.append(signals)
		combined_buylist = pd.Index(all_buylist)
		combined_signals = {}
		for symbol in combined_buylist:
			sym_signals = []
			for signal in all_signals:
				if(symbol in signal):
					sym_signals = [*sym_signals, *signal[symbol]]
			combined_signals[symbol] = sym_signals
		return (combined_signals, combined_buylist)

