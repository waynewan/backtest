# --
# --
# --
from jackutil.microfunc import if_else
from backtest.abc.exitalgo_abc import *
import numpy
import random

# --
# -- sample config
# --
#	"exitalgo:random" : {
#		"cls" : exitalgo_random.exitalgo_random,
#		"opt" : { 
#			"seed" : None, 
#			"threshold" : 0.0004, 
#		}
#	},

class exitalgo_random(exitalgo_abc):
	def __init__(self,*,opt):
		super().__init__()
		self.__last_dt = None
		self.__opt = opt
		self.__threshold = opt['threshold']
		# --
		# -- setup random generator
		# --
		rnd_generator = opt.get('generator','default')
		if(rnd_generator=='SystemRandom'):
			# --
			# !! random.SystemRandom does not support seed
			# !! value and cannot repeat random sequence
			# --
			self.__random = random.SystemRandom().random
		elif(rnd_generator=='custom'):
			# --
			# -- rnd_gen: function that generate random number between [0,1]
			# --
			self.__random = opt['rnd_gen']
		elif(rnd_generator=='numpy'):
			self.__random = numpy.random.rand
			# --
			effective_seed = self.get_random_generator_seed(opt)
			print(f"exitalgo_random/effective_seed:{effective_seed}")
			numpy.random.seed(effective_seed)
		elif(rnd_generator=='default'):
			self.__random = random.random
			# --
			effective_seed = self.get_random_generator_seed(opt)
			print(f"exitalgo_random/effective_seed:{effective_seed}")
			random.seed(effective_seed)

	def get_random_generator_seed(self,opt):
		shared_seed = None
		if('seed' in opt and opt['seed'] is not None):
			shared_seed = opt['seed']
		else:
			# --
			# -- keep old behavior
			# --
			print("exitalgo_random/seed:None")
			return None
		# --
		# -- unique_seed cannot be None
		# --
		unique_seed = 0
		if('useed' in opt and opt['useed'] is not None):
			unique_seed = opt['useed']
		return shared_seed+unique_seed
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
	__roll_exit_cond_name = "random_exit"
	def check_stopout_cond(self,dt,pos,bar):
		return self.check_stopout_for_cond(self.__roll_exit_cond_name,dt,pos,bar)

	def calc_all_exit_conditions(self,dt,pos,bar,bars,universe):
		roll_threshold = self.__threshold
		exit_roll = self.__random()
		stopout_cond_check = if_else(roll_threshold>exit_roll, "exit_roll_exceed_threshold", None)
		# --
		new_value = (roll_threshold,exit_roll,stopout_cond_check is not None,stopout_cond_check)
		curval = pos.exit_conditions[self.__roll_exit_cond_name]
		curval.value = (new_value,dt,None)

