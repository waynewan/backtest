import abc

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

	@abc.abstractmethod
	def calc_all_exit_conditions(self,*,dt,bar,entry_exec_date,entry_price):
		pass

	# --
	# -- common functions
	# --
	def update_map_exit_conditions(self,dt,bar,exec_date,price,xcmap):
		new_conds = self.calc_all_exit_conditions(
			dt=dt,bar=bar,
			entry_exec_date=exec_date,
			entry_price=price
		)
		for kk,nc in new_conds.items():
			self.update_map_exit_condition(xcmap=xcmap,cond_name=kk,**nc)

	def update_map_exit_condition(self,*,xcmap,cond_name,new_val,upd_date,upd_msg=None):
		existing_val = xcmap[cond_name]
		if(not existing_val.hasvalue() or existing_val.value<new_val):
			existing_val.value = (new_val,upd_date,upd_msg)
		
