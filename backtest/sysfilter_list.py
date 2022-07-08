from jackutil.containerutil import cfg_to_obj
from backtest.abc import sysfilter_abc
# --
# --
# --
class sysfilter_list(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		self.__algos = {}
		for key,spec in self.__opt.items():
			self.__algos[key] = cfg_to_obj(opt,key,self.__algos)
	# --
	# --
	# --
	def _read_algos(self): return self.__algos
	algos = property(_read_algos,None,None)
	# --
	# --
	# --
	def _read_opt(self): return self.__opt
	opt = property(_read_opt,None,None)
	# --
	# --
	# --
	def allow_entry(self,dt):
		for key,algo in self.__algos.items():
			result = algo.allow_entry(dt)
			if(result==False):
				return False
		return True

	def allow_exit(self,dt):
		for key,algo in self.__algos.items():
			result = algo.allow_exit(dt)
			if(result==False):
				return False
		return True



