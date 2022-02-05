from jackutil.microfunc import date_only,dt_to_str
from jackutil.auditedvalue import AuditedValue
from . import postprocessor
from collections import defaultdict
from enum import Enum
import pandas as pd

# --
# -- BrokerAccount postprocessors
# -- compute profit, cum-profit; rename some columns
# --
def to_df_pp_old_behavior(acc,df):
	df0 = df.loc[:,(
		'_Position__symbol',
		'entry_exec_date',
		'exit_exec_date'
	)].copy()
	df0.rename(columns={
		'_Position__symbol':'symbol',
		'entry_exec_date':'entry_date',
		'exit_exec_date':'exit_date',
	},inplace=True)
	df0['profit'] = df['share'] * ( df['exit_price'] - df['entry_price'] ) - df['entry_dollar_commission'] - df['exit_dollar_commission']
	df0.sort_values(inplace=True,by='exit_date')
	df0['cumprofit'] = 1 + df0['profit'].cumsum() / acc.init_cash()
	return df0

# --
# --
# --
class PositionState(Enum):
	UNKNOWN = -1
	FAILED = -2
	# --
	STAGED_OPEN = 10
	ACTIVE = 20
	STAGED_CLOSE = 30
	CLOSED = 40
# --
# --
# --
# ==== TODO : a simple tradesim to use BrokerAccount
# ==== TODO : a simple strategy (ie ma crossover) to use tradesim
class TradeSim:
	pass
# --
# --
# --
class BrokerAccount:
	def __init__(self):
		self.__cash = AuditedValue(defval=0.0)
		self.__positions = { s:{} for s in PositionState }

	def deposit(self,*,date,amount,msg):
		assert amount>=0
		#date = __0_date_str__(date)
		new_amount = self.__cash.value + amount
		self.__cash.value = new_amount,date,msg
		return new_amount

	def withdraw(self,*,date,amount,msg):
		assert amount>=0
		#date = __0_date_str__(date)
		new_amount = self.__cash.value - amount
		self.__cash.value = new_amount,date,msg
		return new_amount

	def init_cash(self):
		return self.__cash.audit[0][0]

	def cash_value(self,audit=False):
		if(audit):
			return self.__cash.audit
		else:
			return self.__cash.value

	def positions(self,*states):
		if(states==None or len(states)==0):
			return self.__positions.copy()
		if(len(states)==1):
			return self.__positions[states[0]]
		return { k:v for k,v in self.__positions.items() if k in states }

	def to_dataframe(self,pp=to_df_pp_old_behavior):
		closed = [ pos.__dict__ for pos in self.positions(PositionState.CLOSED).values() ]
		if(len(closed)==0):
			return pd.DataFrame()
		# --
		df = pd.DataFrame(closed)
		if(pp is None):
			return df
		return pp(self,df)

	def stage_open(self,*,date,symbol,msg,signal=None,counter=None):
		new_position = Position(symbol)
		new_position.stage_open(date=date,msg=msg,signal=signal,counter=counter)
		self.__manage_position(new_position)
		return new_position

	def fail_open(self,position,*,date,msg):
		#date = __0_date_str__(date)
		orig_state = position.status
		position.fail_open(date=date,msg=msg)
		self.__manage_position(position,orig_state)

	def stage_close(self,position,*,date,msg,signal=None,counter=None):
		orig_state = position.status
		position.stage_close(date=date,msg=msg,signal=signal,counter=counter)
		self.__manage_position(position,orig_state)

	def try_exec_open(self,position,*,date,share,price,expense,msg):
		if( not position.reduce_staging_counter()):
			return None
		return self.exec_open(position,
			date=date,
			share=share,
			price=price,
			expense=expense,
			msg=msg)

	def exec_open(self,position,*,date,share,price,expense,msg):
		assert share>0
		assert price>=0
		assert expense>=0
		orig_state = position.status
		transaction_cost = position.exec_open(date=date,share=share,price=price,expense=expense,msg=msg)
		self.__manage_position(position,orig_state)
		self.withdraw(date=date,amount=abs(transaction_cost),msg="exec_open {}".format(position))
		return transaction_cost

	def try_exec_close(self,position,*,date,price,expense,msg):
		if( not position.reduce_staging_counter()):
			return None
		return self.exec_close(position,
			date=date,
			price=price,
			expense=expense,
			msg=msg)

	def exec_close(self,position,*,date,price,expense,msg):
		orig_state = position.status
		transaction_cost = position.exec_close(date=date,price=price,expense=expense,msg=msg)
		self.__manage_position(position,orig_state)
		self.deposit(date=date,amount=abs(transaction_cost),msg="exec_close {}".format(position))
		return transaction_cost

	def __manage_position(self,position,orig_state=PositionState.UNKNOWN):
		key = position.__key__()
		if(orig_state !=PositionState.UNKNOWN and position.status !=orig_state):
			orig_store = self.__positions[orig_state]
			if(key in orig_store):
				orig_store.pop(key)
			else:
				raise Exception("{} missing from {}".format(key,orig_state))
		new_store = self.__positions[position.status]
		if(key not in new_store):
			new_store[key] = position
		else:
			raise Exception("{} already in {}".format(key,position.status))

# --
# --
# --
def defdict_init():
	return AuditedValue(defval=0.0)

class Position:
	def __init__(self,symbol,counter=1):
		self.__symbol = symbol
		self.__status = AuditedValue(PositionState.UNKNOWN)
		# self.__exit_conditions = defaultdict(lambda : AuditedValue(defval=0.0))
		self.__exit_conditions = defaultdict(defdict_init)
		self.note = AuditedValue()
		self.__staging_counter = counter
		# --
		self.share = None
		self.entry_dollar_commission = None
		self.entry_exec_date = None
		self.entry_price = None
		self.entry_signal_date = None
		self.exit_dollar_commission = None
		self.exit_exec_date = None
		self.exit_price = None
		self.exit_signal_date = None
		self.entry_signal = None
		self.exit_signal = None

	def expired_staging_counter(self):
		return self.__staging_counter<=0

	def reduce_staging_counter(self):
		self.__staging_counter = self.__staging_counter - 1
		return self.expired_staging_counter()

	def stage_open(self,*,date,msg,signal=None,counter=None):
		assert counter>=0 
		self.entry_signal_date = date
		self.entry_signal = signal
		self.__staging_counter = counter
		self.__status.value = PositionState.STAGED_OPEN,date,msg

	def fail_open(self,*,date,msg):
		self.__status.value = PositionState.FAILED,date,msg

	def exec_open(self,date,share,price,expense,msg):
		self.entry_dollar_commission = expense
		self.entry_exec_date = date
		self.entry_price = price
		self.share = share
		self.__status.value = PositionState.ACTIVE,date,msg
		transaction_cost = -(share * price + expense)
		return transaction_cost
		
	def stage_close(self,*,date,msg,signal=None,counter=None):
		assert counter>=0 
		self.exit_signal_date = date
		self.exit_signal = signal
		self.__staging_counter = counter
		self.__status.value = PositionState.STAGED_CLOSE,date,msg

	def exec_close(self,date,price,expense,msg):
		self.exit_dollar_commission = expense
		self.exit_exec_date = date
		self.exit_price = price
		self.__status.value = PositionState.CLOSED,date,msg
		transaction_cost = -(self.share * price + expense)
		return transaction_cost
		
	@property
	def status_audit(self):
		return self.__status.audit

	@property
	def status(self):
		return self.__status.value

	@property
	def symbol(self):
		return self.__symbol

	@property
	def exit_conditions(self):
		return self.__exit_conditions

	# --
	# -- using "max", only work for long trade
	# --
	def update_exit_condition(self,*,cond_name,new_val,upd_date,upd_msg=None):
		existing_val = self.__exit_conditions[cond_name]
		if(not existing_val.hasvalue() or existing_val.value<new_val):
			existing_val.value = (new_val,upd_date,upd_msg)
		
	def update_exit_conditions(self,new_conds):
		for kk,nc in new_conds.items():
			self.update_exit_condition(cond_name=kk,**nc)

	# --
	# --
	# --
	def __str__(self):
		return "Position({},{},{},{},{},{},{},{},{})".format(
			str(self.entry_signal_date),
			self.__symbol,
			self.share,
			self.__status,
			str(self.entry_exec_date),
			str(self.exit_exec_date),
			str(self.exit_signal_date),
			self.entry_price,
			self.exit_price
		)
	def __repr__(self):
		return "<{}>".format(self.__key__())
	def __format__(self,formatspec=None):
		return "<{}>".format(self.__key__())
	# --
	# --
	# --
	def __key__(self):
		return "Position:{},{}".format( 
			str(self.entry_signal_date), 
			self.__symbol )
	def __hash__(self):
		return hash(self.__key__())
	def __lt__(self,other):
		pass

