import pandas as pd
from jackutil.microfunc import dt64_to_str

def to_dataframe(positions):
	pdict = [ pos.__dict__ for pos in positions ]
	if(len(pdict)==0):
		return pd.DataFrame()
	# --
	return pd.DataFrame(pdict)

def expand_auditedvalue_col(series,*,prefix=None,final_val_only=False,ts_as_index=False):
	if(prefix is None):
		prefix = ""
	elif(prefix[-1] !='_'):
		prefix = prefix + '_'
	if(final_val_only):
		ss = series.apply(lambda x : x.audit[-1] )
		df = pd.DataFrame(ss.to_list(), columns=[prefix+'value',prefix+'ts',prefix+'note'])
		if(ts_as_index):
			df = df.set_index(prefix+'ts')
		return df
	else:
		return series.apply(lambda x : x.audit )

def dump_account(account):
	for kk,vv in account.positions().items():
		if(vv is None):
			print(kk, "[ NONE ]")
		elif(len(vv)==0):
			print(kk, "[ EMPTY ]")
		else:
			print(kk, "#" * 70)
			print(vv)
			print(kk, "#" * 70)

def events_to_dataframe(position,audit_depth=-1):
	status_df = position._Position__status.to_dataframe(limit=audit_depth,marker='_SS_____')
	tstop_df = position.exit_conditions['trailing_stop'].to_dataframe(limit=audit_depth,marker='_____TT_')
	ppstop_df = position.exit_conditions['profit_protect_stop'].to_dataframe(limit=audit_depth,marker='___PP___')
	changes_df = pd.concat([status_df,tstop_df,ppstop_df],axis=0).sort_index()
	return changes_df

def dump_position(position,audit_depth=5):
	print("-- symbol:{0:} --".format(position.symbol))
	print("+ entry[{0:}/{1:}] ${2:.2f} x {3:.3f}".format(
		dt64_to_str(position.entry_signal_date),
		dt64_to_str(position.entry_exec_date),
		position.entry_price,
		position.share
	))
	print("+ exit[{0:}/{1:}] ${2:.2f} x {3:.3f}".format(
		dt64_to_str(position.exit_signal_date),
		dt64_to_str(position.exit_exec_date),
		position.exit_price,
		position.share
	))
	ttl_commission = position.entry_dollar_commission+position.exit_dollar_commission
	p_and_l = position.share * (position.exit_price - position.entry_price) - ttl_commission 
	print("+ commission: ${0:.2f}".format(ttl_commission))
	print("+ P&L: ${0:.2f}".format(p_and_l))
	if(audit_depth>0):
		sl = slice(0,audit_depth,1)
		if(audit_depth==-1):
			sl = slice(None,None,None)
		print("+ status:",len(position.status_audit))
		for ss in position.status_audit[sl]:
			print("├── {1:8s} {0:} [{2:}]".format(*ss))
		print("+ trailing_stop:",len(position.exit_conditions['trailing_stop'].audit))
		for ss in position.exit_conditions['trailing_stop'].audit[sl]:
			print("├── {1:8s} {0:} [{2:}]".format(*ss))
		print("+ profit_protect_stop:",len(position.exit_conditions['profit_protect_stop'].audit))
		for ss in position.exit_conditions['profit_protect_stop'].audit[sl]:
			print("├── {1:8s} {0:} [{2:}]".format(*ss))
