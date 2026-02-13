from jackutil.containerutil import cfg_to_obj
from jackutil.microfunc import inrange,callable_fq_name,concat_lists,default_val
from backtest.abc.entryalgo_abc import entryalgo_abc
import pandas as pd

# --
# --
# --
def def_aggr(a_all_buylist):
	all_buylist = []
	for buylist in a_all_buylist:
		all_buylist = concat_lists(all_buylist,buylist)
	return all_buylist
# --
# --
# --
class entryalgo_collab(entryalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__keys = [ x for x in self.__opt['objs'] if(not x.startswith("__")) ]
		self.__algos = { key:None for key in set(self.__keys) }
		self.__aggregator = default_val(self.__opt.get('aggregator'),def_aggr)
		# -- DEBUG -- print(self.__aggregator)

	def link(self,linker):
		for key in self.__keys:
			self.__algos[key] = linker(key)
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
		for key in self.__keys:
			algo = self.__algos[key]
			pp_opt = [ *pp_opt, *algo.postprocessor() ]
		return pp_opt

	def exec_open_final_check(self,symbol,bar):
		for key in self.__keys:
			algo = self.__algos[key]
			msg = algo.exec_open_final_check(symbol,bar)
			if(msg is not None):
				return msg
		return None

	def buy_list_on(self,dt,bars,universe):
		all_signals = []
		all_buylist = []
		for key in self.__keys:
			algo = self.__algos[key]
			(signals, buylist) = algo.buy_list_on(dt,bars,universe)
			all_buylist.append(buylist)
			all_signals.append(signals)
		all_buylist = self.__aggregator(all_buylist)
		combined_buylist = pd.Index(all_buylist)
		combined_signals = {}
		for symbol in combined_buylist:
			sym_signals = []
			for signal in all_signals:
				if(symbol in signal):
					new_signal = signal[symbol]
					sym_signals = [*sym_signals, new_signal]
			combined_signals[symbol] = sym_signals
		return (combined_signals, combined_buylist)

