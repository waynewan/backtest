import pandas as pd
import numpy as np

# --
# -- dataload postprocessors
# -- generic util
# -- add a column (constant value only)
# --
def pp_util_add_columns(symbol,data,**kv):
	for k,v in kv.items():
		data[k] = v
	return data

# --
# -- dataload postprocessors
# -- common TA algorithm 
# -- classic moving average cross over/under
# --
def pp_ta_ma_cross(symbol,data,*,lperiod=200,speriod=50):
	data['ma_lp'] = data['Close'].rolling(lperiod).mean()
	data['ma_sp']  = data['Close'].rolling(speriod).mean()
	l_lt_s = data['ma_lp']>data['ma_sp']
	data['golden_cross'] = (~l_lt_s).shift(1) & l_lt_s
	data['death_cross'] = l_lt_s.shift(1) & ~l_lt_s
	return data

# --
# -- BrokerAccount postprocessors
# -- compute profit, cum-profit
# --
def to_df_pp_basic(acc,df):
	df['profit'] = df['share'] * ( df['exit_price'] - df['entry_price'] ) - df['entry_dollar_commission'] - df['exit_dollar_commission']
	df['pgain'] = ( df['share'] * df['exit_price'] - df['exit_dollar_commission'] ) / ( df['share'] * df['entry_price'] + df['entry_dollar_commission'] ) - 1.0
	df.sort_values(inplace=True,by='exit_exec_date')
	df['cumprofit'] = 1 + df['profit'].cumsum() / acc.init_cash()
	return df

