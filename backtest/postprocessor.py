import pandas as pd
import numpy as np
# -- need anacoda upgrade first -- import talib as ta

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
# -- compute ATR using TA-lib
# --
# -- need anacoda upgrade first -- def pp_ta_atr(symbol,data,*,lperiod=252):
# -- need anacoda upgrade first -- 	high_vals = data['High'].values.astype('double')
# -- need anacoda upgrade first -- 	low_vals = data['Low'].values.astype('double')
# -- need anacoda upgrade first -- 	close_vals = data['Close'].values.astype('double')
# -- need anacoda upgrade first -- 	atr_vals = ta.ATR( high_vals, low_vals, close_vals, timeperiod=lperiod)
# -- need anacoda upgrade first -- 	data['atr'] = pd.Series(index=data.index,data=atr_vals)
# -- need anacoda upgrade first -- 	return data

# --
# ** BrokerAccount postprocessors
# ** compute profit, cum-profit
# --
def to_df_pp_basic(acc,df):
	df['profit'] = df['share'] * ( df['exit_price'] - df['entry_price'] ) - df['entry_dollar_commission'] - df['exit_dollar_commission']
	# --
	# -- pgain cannot be cumprod, because the trades overlap
	# --
	df['pgain'] = ( df['share'] * df['exit_price'] - df['exit_dollar_commission'] ) / ( df['share'] * df['entry_price'] + df['entry_dollar_commission'] ) - 1.0
	df.sort_values(inplace=True,by='exit_exec_date')
	df['cumprofit'] = 1 + df['profit'].cumsum() / acc.init_cash()
	return df

