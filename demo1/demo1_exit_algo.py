from jackutil.microfunc import callable_fq_name
from backtest.exitalgo_abc import exitalgo_abc
from backtest import norgate_helper
import pandas as pd
import numpy as np

def pp_barlen(symbol,data,*,period,multiple,max_pct_risk):
    solid_bar_len = np.abs( data['Open'] - data['Close'] )
    average = solid_bar_len.rolling(period).mean()
    stderr = solid_bar_len.rolling(period).std()
    orig_dollar_risk = average + multiple * stderr
    dollar_risk = np.minimum(data["Close"] * max_pct_risk, orig_dollar_risk)
    data['dollar_risk'] = dollar_risk
    data['dollar_stop'] = data['Open'] - data['dollar_risk']

# --
# --
# --
class demo1_exit_algo(exitalgo_abc):
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
			[ callable_fq_name(pp_barlen),self.__opt['pp'] ],
		]
		return pp_opt

	# --
	# -- return reason string if exit triggered
	# -- otherwise, return None
	# --
	def check_stopout_cond(self,dt,pos,bar):
		if(bar['note']=='LAST_BAR'):
			return "end_of_listing"
		if(bar['Close']<pos.trailing_stop):
			return "below_trailing_stop"
		if(bar['Close']<pos.profit_protect_stop):
			return "below_profit_protect_stop"
		return None

	def update_trailing_stop_for(self,dt,pos,bar):
		rt_cfg = self.__opt["op"]
		# --
		# !! only have access to 1 position at a time !!
		# !! cannot scale based on position account   !!
		current_position_count = 1
		# @@ CONFIG_update_trailing_stoploss_positions_count = True 
		# @@ if(CONFIG_update_trailing_stoploss_positions_count):
		# @@ 	current_position_count = len( account['positions'] )
		position_age = (dt - pos.entry_exec_date)/np.timedelta64(1,'D') * 5 / 7
		age_adj_factor = max(0.01, 1 - (current_position_count * position_age**2) / (rt_cfg['max_age']**2))
		dollar_risk_offset = bar['dollar_stop'] + bar['dollar_risk']
		age_adj_dollar_stop = dollar_risk_offset - bar['dollar_risk'] * age_adj_factor
		actual_dollar_stop = max(age_adj_dollar_stop, bar['dollar_stop'])
		new_stop = max(bar['dollar_stop'], age_adj_dollar_stop)
		pos.update_trailing_stop(date=dt,new_stop=new_stop,msg=None)
		# --
		# --
		# --
		curr_gain = bar['Close'] / pos.entry_price
		factor = 0
		if(curr_gain > 1.5):
			factor = 1.25
		elif(curr_gain >= 1.25):
			factor = 1
		new_stop = pos.entry_price * factor
		pos.update_profit_protect_stop(date=dt,new_stop=new_stop,msg=None)

