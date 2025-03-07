# --
# --
# --
from jackutil.microfunc import if_else,dt_conv
from backtest.abc.exitalgo_abc import *
from pprint import pprint
import numpy

# --
# -- sample config
# --
#	"exitalgo:instruction1" : {
#		"cls" : exitalgo_manual.exitalgo_manual,
#		"opt" : { 
#			"instructions" : [
#				{ "symbol" : "X", "max_trig" : 5, },
#				{ "symbol" : "P", "quantity" : (30,50) },
#				{ "symbol" : "M", "entry_date" : ("2025-01-03","2025-01-31") },
#				{ "symbol" : "K", "entry_date" : "2025-01-03" },
#			]
#		}
#	},

class exitalgo_manual(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__last_dt = None
		self.__opt = opt
		self.__pos_set = set()
		self.__instructions = opt['instructions']
		# --
		# -- init all instructions' max_trig if not defined
		# --
		for instr in self.__instructions:
			instr["max_trig"] = instr.get("max_trig",9999)
		if(self.__instructions):
			print("########################################")
			print("# instructions")
			pprint(self.__instructions)
			print("########################################")
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
		]
		return pp_opt

	# --
	# --
	# --
	__manual_exit_cond_name = "manual_exit"
	def check_stopout_cond(self,dt,pos,bar):
		return self.check_stopout_for_cond(self.__manual_exit_cond_name,dt,pos,bar)

	def exit_cond_check_symbol(self,pos_symbol,instr_symbol):
		if(pos_symbol is None):
			raise ValueError("position symbol cannot be None")
		if(instr_symbol is None):
			return True
		if(type(instr_symbol)==type("") and pos_symbol==instr_symbol):
			return True
		if(type(instr_symbol)==type(()) or type(instr_symbol)==type([]) ):
			return pos_symbol in instr_symbol
		return False

	def exit_cond_check_entry_date(self,pos_entry_date,instr_entry_date):
		if(pos_entry_date is None):
			raise ValueError("position entry_date cannot be None")
		if(instr_entry_date is None):
			return True
		# --
		pos_entry_date = dt_conv(from_val=pos_entry_date,to_type="dt64")
		if(type(instr_entry_date)==type(()) or type(instr_entry_date)==type([]) ):
			range_beg = dt_conv(from_val=instr_entry_date[0],to_type="dt64")
			range_end = dt_conv(from_val=instr_entry_date[1],to_type="dt64")
			return range_beg <= pos_entry_date < range_end
		# --
		# !! assume simple case, either str or date type
		# --
		instr_entry_date = dt_conv(from_val=instr_entry_date,to_type="dt64")
		return pos_entry_date==instr_entry_date

	def exit_cond_check_quantity(self,pos_quantity,instr_quantity):
		if(pos_quantity is None):
			raise ValueError("position quantity cannot be None")
		if(instr_quantity is None):
			return True
		if(type(instr_quantity)==type(()) or type(instr_quantity)==type([]) ):
			return instr_quantity[0] <= pos_quantity < instr_quantity[1]
		return pos_quantity==instr_quantity

	def exit_cond_check_pos(self,pos,instr):
		# print( pos, instr, self.exit_cond_check_symbol(pos.symbol,instr.get('symbol',None)) )
		# print( pos, instr, self.exit_cond_check_entry_date(pos.entry_exec_date,instr.get('entry_date',None)) )
		# print( pos, instr, self.exit_cond_check_quantity(pos.share,instr.get('quantity',None)) )
		return \
			self.exit_cond_check_symbol(pos.symbol,instr.get('symbol',None)) \
			and self.exit_cond_check_entry_date(pos.entry_exec_date,instr.get('entry_date',None)) \
			and self.exit_cond_check_quantity(pos.share,instr.get('quantity',None))
		
	def once_only_with_each_pos(self,pos,fn):
		if(pos in self.__pos_set):
			return
		self.__pos_set.add(pos)
		return fn()
		
	def find_matcing_instr(self,pos):
		for instr in self.__instructions:
			if(instr["max_trig"]>0):
				instr_matched = self.exit_cond_check_pos(pos,instr)
				if(instr_matched):
					instr['max_trig'] -= 1
					return pos,True
		return pos,False

	def update_pos_exit_cond(self,dt,pos,matched):
		new_value = (False,None)
		if(matched):
			new_value = (True,self.__manual_exit_cond_name)
		self.update_pos_exit_condition_chandelier(pos,self.__manual_exit_cond_name,new_value,dt,None)
		
	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		self.once_only_with_each_pos(pos, 
			lambda:
				self.update_pos_exit_cond(
					dt, *self.find_matcing_instr(pos)
				)
		)

