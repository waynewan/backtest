import abc
from enum import Enum

class exitalgo_abc(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self):
		pass

	@abc.abstractmethod
	def postprocessor(self):
		pass

	# --
	# -- return reason string if exit triggered
	# -- otherwise, return None
	# --
	@abc.abstractmethod
	def check_stopout_cond(self,dt,pos,bar):
		pass

	def check_stopout_for_cond(self,cond,dt,pos,bar):
		exit_cond = pos.exit_conditions[cond].value
		return exit_cond[-1]

	@abc.abstractmethod
	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		pass

	# --
	# -- call by calc_all_exit_conditions only
	# --
	def update_pos_exit_condition_chandelier(self,pos,cond_name,new_val,upd_date,upd_msg):
		curval = pos.exit_conditions[cond_name]
		if(not curval.hasvalue() or curval.value<new_val):
			curval.value = (new_val,upd_date,upd_msg)

	def update_pos_exit_condition_rev_chandelier(self,pos,cond_name,new_val,upd_date,upd_msg):
		curval = pos.exit_conditions[cond_name]
		if(not curval.hasvalue() or curval.value>new_val):
			curval.value = (new_val,upd_date,upd_msg)

	def update_pos_exit_condition_last(self,existing_val,cond_name,new_val,upd_date,upd_msg):
		curval = pos.exit_conditions[cond_name]
		curval.value = new_val

	# --
	# !! it will be very inefficient to use this if value is only set once !!
	# !! instead, use this as a template                                   !!
	# --
	def update_pos_exit_condition_first(self,pos,cond_name,new_val,upd_date,upd_msg):
		curval = pos.exit_conditions[cond_name]
		if(curval.hasvalue()):
			return
		curval.value = new_val

