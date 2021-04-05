import functools
import pickle
import os
from jackutil.containerutil import containerChecksum

class TradesimStore:
	def __init__(self,path="./Tradesim",overwrite=False,flag_spec=True,flag_account=True,flag_d0=False,flag_universe=False):
		self.__storepath=path
		self.__overwrite=overwrite
		self.__flag_account=flag_account
		self.__flag_d0=flag_d0
		self.__flag_universe=flag_universe
		self.__flag_spec=flag_spec

	def fullpaths(self,rtspec):
		hashcode = containerChecksum(rtspec)
		path = self.storepath
		return (
			f"{path}/{hashcode}.account_pickle",
			f"{path}/{hashcode}.d0_pickle",
			f"{path}/{hashcode}.universe_pickle",
			f"{path}/{hashcode}.spec_pickle",
		)
	
	def has(self,rtspec):
		fp_account,fp_d0,fp_universe,fp_spec = self.fullpaths(rtspec)
		has_account = None
		if(self.__flag_account):
			has_account = os.path.isfile(fp_account)
		has_d0 = None
		if(self.__flag_d0):
			has_d0 = os.path.isfile(fp_d0)
		has_universe = None
		if(self.__flag_universe):
			has_universe = os.path.isfile(fp_universe)
		has_spec = None
		if(self.__flag_spec):
			has_spec = os.path.isfile(fp_spec)
		return (has_account,has_d0,has_universe,has_spec)

	def _store_data_at_(self,fullpath,data,overwrite):
		if(not overwrite and os.path.isfile(fullpath)):
			raise Exception('file exist',fullpath)
		with open(fullpath,"wb") as file:
			pickle.dump(data,file)
		
	@functools.lru_cache(maxsize=8000)
	def _read_data_at_(self,fullpath,flag):
		if(flag):
			with open(fullpath,"rb") as file:
				obj = pickle.load(file)
				return obj
		return None

	def store(self,rtspec,*,account,d0,universe):
		fp_account,fp_d0,fp_universe,fp_spec = self.fullpaths(rtspec)
		if(account is not None and self.flag_account):
			self._store_data_at_(fp_account,account,self.__overwrite)
		if(d0 is not None and self.flag_d0):
			self._store_data_at_(fp_d0,d0,self.__overwrite)
		if(universe is not None and self.flag_universe):
			self._store_data_at_(fp_universe,universe,self.__overwrite)
		if(rtspec is not None and self.flag_spec):
			self._store_data_at_(fp_spec,rtspec,self.__overwrite)

	def load(self,rtspec):
		fp_account,fp_d0,fp_universe,fp_spec = self.fullpaths(rtspec)
		return (
			self._read_data_at_(fp_account,self.__flag_account),
			self._read_data_at_(fp_d0,self.__flag_d0),
			self._read_data_at_(fp_universe,self.__flag_universe),
			self._read_data_at_(fp_spec,self.__flag_spec),
		)
	# --
	# --
	# --
	def _read_storepath(self):
		return self.__storepath
	storepath = property(_read_storepath,None,None)
	def _read_overwrite(self):
		return self.__overwrite
	overwrite = property(_read_overwrite,None,None)
	def _read_flag_account(self):
		return self.__flag_account
	flag_account = property(_read_flag_account,None,None)
	def _read_flag_d0(self):
		return self.__flag_d0
	flag_d0 = property(_read_flag_d0,None,None)
	def _read_flag_universe(self):
		return self.__flag_universe
	flag_universe = property(_read_flag_universe,None,None)
	def _read_flag_spec(self):
		return self.__flag_spec
	flag_spec = property(_read_flag_spec,None,None)
	# --
	# --
	# --

if(__name__=='__main__'):
	print("running file as script ... ")
	tss = TradesimStore()

