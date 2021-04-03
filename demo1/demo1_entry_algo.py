from jackutil.microfunc import inrange,callable_fq_name
from backtest.entryalgo_abc import entryalgo_abc
from backtest import norgate_helper
from backtest import postprocessor
import pandas as pd
import numpy as np

def pp_ta_ma_cross(symbol,data,*,lperiod=200,speriod=50):
	data['ratio'] = data['Close'].rolling(lperiod).mean() / data['Close'].rolling(speriod).mean()
	return data
# --
# --
# --
class demo1_entry_algo(entryalgo_abc):
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
			[ callable_fq_name(pp_ta_ma_cross),self.__opt['pp'] ],
		]
		return pp_opt

	def capture_signals(self,prcvolavgOrd,bars):
		signals = {}
		for symbol in prcvolavgOrd:
			bar = bars.loc[symbol]
			signals[symbol] = ( bar['ratio'] )
		return signals

	# --
	# 1,3,5,2,4,6 -- R1k=35x,S500=65x,N100=116x
	# 1,2,3,4,5,6 -- R1k=65x,S500=55x,N100=123x
	# !! the first sequence makes more sense, 
	# !! because it eliminates all unwanted symbols first
	# !! the poor performance of R1k is a flute, if mapos +/-1
	# --
	def buy_list_on(self,dt,bars,universe):
		rt_cfg = self.__opt["op"]
		EMPTY_topCandidates_Return=({},pd.Series([],dtype='str'))
		# --
		# -- (1) remove symbols not in index#pit
		# --
		u1 = universe.symbols_at(dt)
		dOnly = bars.loc[u1]
		if(len(dOnly)==0):
			return EMPTY_topCandidates_Return
		# --
		# -- (2) only keep symbol with +ve ratio
		# --
		ratioCol = dOnly.loc[:,'ratio']
		ratiofiltered = ratioCol[ratioCol>0].index
		dOnly = dOnly.loc[ratiofiltered]
		if(len(dOnly)==0):
			return EMPTY_topCandidates_Return
		# --
		# -- (3) sort by ratio, higher is better
		# --
		ratioOrd = dOnly.loc[:,'ratio'].sort_values(ascending=False,na_position="last").index
		signals = self.capture_signals(ratioOrd,bars)
		return (signals,ratioOrd)

