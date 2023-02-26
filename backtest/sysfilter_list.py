from jackutil.containerutil import cfg_to_obj
from backtest.abc import sysfilter_abc
# --
# --
# --
class sysfilter_list(sysfilter_abc.sysfilter_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__opt = opt
		keys = filter(lambda x:not x.startswith("__"), self.__opt['objs'])
		self.__algos = { key:None for key in set(keys) }

	def link(self,linker):
		for key in self.__algos.keys():
			self.__algos[key] = linker(key)
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



