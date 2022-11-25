import math
import datetime
import pandas as pd
from tqdm.auto import tqdm
from backtest.abc.tradesim_abc import tradesim_abc
from .account import BrokerAccount,PositionState,Position
from collections import defaultdict
from jackutil.auditedvalue import AuditedValue

class Tradesim(tradesim_abc):
	def __init__(self,*,entryalgo,exitalgo,universe,sysfilter,opt):
		super().__init__()
		self.__maxpos = opt["maxpos"]
		self.__expense_ratio = opt["expense_ratio"]
		self.__init_capital= opt["init_capital"]
		self.__entry_delay = opt["entry_delay"]
		self.__exit_delay = opt["exit_delay"]
		self.__entryalgo = entryalgo
		self.__exitalgo = exitalgo
		self.__universe = universe
		self.__sysfilter = sysfilter
		self.__logger = self._tradesim_abc__logger

	# --
	# --
	# --
	def _read_maxpos(self): return self.__maxpos
	maxpos = property(_read_maxpos,None,None)
	def _read_expense_ratio(self): return self.__expense_ratio
	expense_ratio = property(_read_expense_ratio,None,None)
	def _read_init_capital(self): return self.__init_capital
	init_capital = property(_read_init_capital,None,None)
	def _read_entryalgo(self): return self.__entryalgo
	entryalgo = property(_read_entryalgo,None,None)
	def _read_exitalgo(self): return self.__exitalgo
	exitalgo = property(_read_exitalgo,None,None)
	def _read_universe(self): return self.__universe
	universe = property(_read_universe,None,None)
	def _read_sysfilter(self): return self.__sysfilter
	sysfilter = property(_read_sysfilter,None,None)
	# --
	# --
	# --
	def runBacktest(self):
		account = BrokerAccount()
		account.deposit(date=self.__universe.first_trade_date,amount=self.__init_capital,msg='init funding')
		# --
		for dt in tqdm(self.__universe.trade_dates,leave=None,desc="backtesting"):
			try:
				self.__universe.asof_date = dt
				bars = self.__universe.bars_on(dt)
				if(self.__universe.is_last_trade_date(dt)):
					self.close_all_positions(dt,account,bars)
				else:
					self.process_bars(dt,account,bars)
			except Exception as ex:
				print(dt,ex)
				raise
		return account,self.__universe.d0,self.__universe

	def fail_staged_open(self,dt,account,bars,msg):
		staged_open = tuple( account.positions(PositionState.STAGED_OPEN).values() )
		for pos in staged_open:
			account.fail_open(pos,date=dt,msg=msg)

	def stage_open_from_strategy(self,dt,account,bars):
		buy_list = self.__entryalgo.buy_list_on(dt,bars,self.__universe)
		self.__logger.debug("buy_list: dt=%s; sym=%s", dt, buy_list[1].tolist())
		for uid,symbol in enumerate(buy_list[1]):
			signal = buy_list[0][symbol]
			account.stage_open(
				date=dt,
				uid=uid,
				symbol=symbol,
				msg='buy_list',
				signal=signal,
				counter=self.__entry_delay)

	def internal__check_stopout_cond(self,dt,pos,bar):
		if(bar['last_n_bar']>self.__exit_delay):
			return self.__exitalgo.check_stopout_cond(dt,pos,bar)
		if(bar['last_n_bar']==self.__exit_delay):
			return "end_of_listing"
		elif(bar['last_n_bar']<self.__exit_delay):
			errmsg = "last_n_bar({}) is less than exit_delay({}); pos={}".format(
				bar['last_n_bar'],self.__exit_delay,pos
			)
			raise RuntimeError(errmsg)
			# print(errmsg)
			# return "end_of_listing"

	def stage_close_from_strategy(self,dt,account,bars):
		active_trades = tuple( account.positions(PositionState.ACTIVE).values() )
		for pos in active_trades:
			bar = bars.loc[pos.symbol]
			stopout_msg = self.internal__check_stopout_cond(dt,pos,bar)
			if(stopout_msg is not None):
				self.__logger.debug("stopout: dt=%s; sym=%s; reason=%s", dt, pos.symbol, stopout_msg)
				account.stage_close(pos,date=dt,msg=stopout_msg,counter=self.__exit_delay)

	# --
	# -- chandelier all exit
	# --
	def update_pos_exit_conditions(self,dt,pos,bar,bars):
		new_conds = self.__exitalgo.calc_all_exit_conditions(
			dt=dt,pos=pos,
			bar=bar,bars=bars,
			universe=self.__universe,
			sysfilter=self.__sysfilter,
		)
		for kk,nc in new_conds.items():
			self.update_pos_exit_condition(xcmap=pos.exit_conditions,cond_name=kk,**nc)

	def update_pos_exit_condition(self,*,xcmap,cond_name,new_val,upd_date,upd_msg=None):
		existing_val = xcmap[cond_name]
		if(not existing_val.hasvalue() or existing_val.value<new_val):
			self.__logger.debug("updated stop name=%s, old=%s, new=%s", cond_name, existing_val.value, new_val)
			existing_val.value = (new_val,upd_date,upd_msg)
		
	def update_account_exit_conditions(self,dt,account,bars):
		for pos in account.positions(PositionState.ACTIVE).values():
			bar = bars.loc[pos.symbol]
			self.update_pos_exit_conditions( dt,pos,bar,bars )
	
	def flush_stagged_open_no_allow(self,dt,account,bars):
		staged_open = tuple( account.positions(PositionState.STAGED_OPEN).values() )
		for ii,pos in enumerate(staged_open):
			account.fail_open(pos,date=dt,msg="no_exec_open_allowed")
		
	def internal__exec_open_final_check(self,symbol,bar):
		last_n_bar = bar['last_n_bar']
		if(last_n_bar>self.__exit_delay and last_n_bar>self.__entry_delay):
			return self.__entryalgo.exec_open_final_check(symbol,bar)
		else:
			return "end_of_listing"

	def exec_or_fail_stagged_open(self,dt,account,bars):
		max_new_pos_count = self.__maxpos - len( account.positions(PositionState.ACTIVE) )
		new_position_dollar_amt = account.cash_value() / max(1,max_new_pos_count) * (1 - self.__expense_ratio )
		exec_stagged_open_msg = "exec_stagged_open@{}".format(new_position_dollar_amt)
		staged_open = tuple( account.positions(PositionState.STAGED_OPEN).values() )
		for ii,pos in enumerate(staged_open):
			if(ii>=max_new_pos_count):
				account.fail_open(pos,date=dt,msg="reach_max_position")
			elif(new_position_dollar_amt<=0):
				account.fail_open(pos,date=dt,msg="negative_cash_value")
			else:
				final_check_fail_reason = self.internal__exec_open_final_check(pos.symbol,bars.loc[pos.symbol])
				if(final_check_fail_reason is not None):
					account.fail_open(pos,date=dt,msg=final_check_fail_reason)
					return
				# --
				close_price = bars.loc[pos.symbol,'Close']
				if(math.isnan(close_price)):
					account.fail_open(pos,date=dt,msg="missing_price")
				elif(math.isnan(new_position_dollar_amt)):
					account.fail_open(pos,date=dt,msg="invalid_dollar_amt")
				elif(new_position_dollar_amt<=0):
					account.fail_open(pos,date=dt,msg="not_enough_capital")
				else:
					# !!
					# !! rounding should be optional, 
					# !! if rounding apply, unadj close should be used 
					# !!
					share = new_position_dollar_amt / close_price 
					net_gross = close_price * share
					commission = round(net_gross * self.__expense_ratio, 2)
					account.try_exec_open(pos,date=dt,share=share,price=close_price,expense=commission,msg=exec_stagged_open_msg)

	def exec_close_on_state(self,dt,state,account,bars,msg,stage_and_close=False,force_close=False):
		stage_close = tuple( account.positions(state).values() )
		for pos in stage_close:
			close_price = bars.loc[pos.symbol,'Close']
			share = pos.share
			commission = round(close_price * share * self.__expense_ratio, 2)
			if(stage_and_close):
				account.stage_close(pos,date=dt,msg="stage_and_close",counter=0)
				account.exec_close(pos,date=dt,price=close_price,expense=commission,msg=msg)
			elif(force_close):
				account.exec_close(pos,date=dt,price=close_price,expense=commission,msg=msg)
			else:
				account.try_exec_close(pos,date=dt,price=close_price,expense=commission,msg=msg)

	def close_all_positions(self,dt,account,bars):
		self.fail_staged_open(dt,account,bars,"last_session")
		staged_open = tuple( account.positions(PositionState.STAGED_OPEN).values() )
		for pos in staged_open:
			account.fail_open(pos,date=dt,msg='last_session')
		self.exec_close_on_state(dt,PositionState.ACTIVE,account,bars,"last_session",stage_and_close=True)
		self.exec_close_on_state(dt,PositionState.STAGED_CLOSE,account,bars,"last_session",force_close=True)

	def process_bars(self,dt,account,bars):
		# --
		# -- trade_at_eod: reclaim capital by exec stagged close
		# --
		if(self.__sysfilter.allow_exit(dt)):
			self.exec_close_on_state(dt,PositionState.STAGED_CLOSE,account,bars,"stagged_close_exec")
		# --
		# -- exec stagged positions from previous bar (not bars)
		# -- discard any stagged that are not exec'ed
		# --
		self.exec_or_fail_stagged_open(dt,account,bars)
		# --
		# -- stage (but not exec) new trades, based on EOD data
		# --
		if(self.__sysfilter.allow_entry(dt)):
			self.stage_open_from_strategy(dt,account,bars)
		# --
		# -- update trailing stop for next cycle
		# !! ==> close exec base on the latest available information
		# !!     because execution is always delay by at least 1 period
		# --
		self.update_account_exit_conditions(dt,account,bars)
		# --
		# -- check for any trade need to be closed
		# --
		self.stage_close_from_strategy(dt,account,bars)

	# --
	# -- below, queries only
	# --
	def runDailyAction(self,days=1):
		result = []
		for dt64 in self.__universe.trade_dates[-days:]:
			daily_action = {
				"rundate"    : dt64,
				"sysfilter"  : {
					"allow_entry" : self.__sysfilter.allow_entry(dt64),
					"allow_exit" : self.__sysfilter.allow_exit(dt64),
				},
				"stageopen"  : self.__genDailyBuyList(dt64),
				"stageclose" : self.__genDailySellList(dt64),
			}
			result.append(daily_action)
		return result

	def __genDailyBuyList(self,dt64):
		self.__universe.asof_date = dt64
		bars = self.__universe.bars_on(dt64)
		if(self.__sysfilter.allow_entry(dt64)):
			return self.__entryalgo.buy_list_on(dt64,bars,self.__universe)
		else:
			EMPTY_topCandidates_Return=({},pd.Series([],dtype='str'))
			return EMPTY_topCandidates_Return

	def __genDailySellList(self,dt64):
		return [ 'NOT_IMPL' ]

	def __exec_to_pos(self,exec):
		pos = Position(exec['uid'], exec['symbol'])
		pos.entry_exec_date = exec['entry_exec_date']
		pos.entry_price = exec['entry_price']
		return pos

	def calcTrailingstop(self,executions):
		pos_cache = {}
		for dt in tqdm(self.__universe.trade_dates,leave=None,desc="calcTrailingstop"):
			bars = self.__universe.bars_on(dt)
			for exec in executions: # tqdm(executions,leave=None,desc="executions"):
				exec_date = exec['entry_exec_date']
				if(dt<exec_date):
					continue
				if(not exec['action'] or exec['action'] !='BUY'):
					continue
				bar = bars.loc[exec['symbol']]
				# --
				key = ( exec['uid'], exec['symbol'], exec['entry_exec_date'], exec['entry_price'] )
				if(key not in pos_cache): pos_cache[key] = self.__exec_to_pos(exec)
				pos = pos_cache[key]
				# --
				self.update_pos_exit_conditions( dt,pos,bar,bars )
				exec['stops'] = pos.exit_conditions

