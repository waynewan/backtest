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
	def calc_all_exit_conditions(self,*,dt,pos,bar,bars,universe):
		pass

	# --
	# -- common functions
	# --
	def update_map_exit_conditions(self,dt,pos,bar,bars,universe): #,exec_date,price):
		new_conds = self.calc_all_exit_conditions(
			dt=dt,pos=pos,
			bar=bar,bars=bars,
			universe=universe
		)
		for kk,nc in new_conds.items():
			self.update_map_exit_condition(xcmap=pos.exit_conditions,cond_name=kk,**nc)

	def update_map_exit_condition(self,*,xcmap,cond_name,new_val,upd_date,upd_msg=None):
		existing_val = xcmap[cond_name]
		if(not existing_val.hasvalue() or existing_val.value<new_val):
			existing_val.value = (new_val,upd_date,upd_msg)
		
