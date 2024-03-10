# --
# --
# --
import sys
sys.path.append("../../../common/lib/trade_secret_algo")
import algo_codelet_talib0 as codelet
# --
# --
# --
from jackutil.microfunc import inrange,callable_fq_name
from backtest.abc.entryalgo_abc import entryalgo_abc
from backtest import norgate_helper
import pandas as pd
import numpy as np
import scipy.stats as stats

def pp_1(symbol,data,seed):
	data['score'] = np.random.rand(data.shape[0])
	return data

class entryalgo_random(entryalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
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
			# --
			# -- the "seed" is a dummy, but needed to force new random seq
			# --
			[ callable_fq_name(pp_1),{"seed" : self.__opt['seed']} ],
		]
		return pp_opt

	def exec_open_final_check(self,symbol,bar):
		return None

	def capture_signals(self,prcvolavgOrd,bars):
		signals = {}
		for symbol in prcvolavgOrd:
			bar = bars.loc[symbol]
			signals[symbol] = ( bar['Uclose'] )
		return signals

	# --
	# --
	# --
	def buy_list_on(self,dt,bars,universe):
		rt_cfg = self.__opt["op"]
		EMPTY_topCandidates_Return=({},pd.Series([],dtype='str'))
		# --
		dOnly = codelet.init_dOnly(dt,bars,universe)
		if('q_uclose' in rt_cfg):
			dOnly = codelet.filter_by_col_qrange(dOnly,'Uclose',rt_cfg['q_uclose'])
		if('min_uclose' in rt_cfg):
			dOnly = codelet.filter_by_apply(dOnly,'Uclose',lambda p: p>=rt_cfg['min_uclose'])
		# --
		if(len(dOnly)==0):
			return EMPTY_topCandidates_Return
		# --
		candidates = codelet.sort_and_return(dOnly,'score',max_rtn=rt_cfg['max_rtn'],ascending=False)
		signals = self.capture_signals(candidates,bars)
		return (signals,candidates)
