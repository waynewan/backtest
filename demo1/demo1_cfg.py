from jackutil.microfunc import str_to_dt
from jackutil.configuration import configuration
from backtest import tradesim,norgate_helper
from backtest.defimpl import index_universe
import numpy as np
import demo1_entry_algo,demo1_exit_algo,demo1_sysfilter

# --
# -- index specific setup
# --
index_specific_setup = {
	(
		"universe/opt/indexname",
		"sysfilter/opt/symbol",
		"entryalgo/opt/op/q_pvachgratio/0"
	) : [ 
		("NASDAQ 100",  "QQQ", 0.5), 
		("S&P 500",     "SPY", 0.8), 
		("Russell 1000","IWB", 0.8),
	],
}
index_specs = configuration(basespec={},variations=index_specific_setup)
n100spec,s500spec,r1000spec = index_specs.all_variations()

# --
# -- boiler plate
# -- "pp" -- bar loading postprocessor
# -- "op" -- object operating option
# --
basespec = {
	"simulator" : {
		"cls" : tradesim.Tradesim,
		"opt" : {
			"maxpos" : 30,
			"expense_ratio" : 0.5 / 100,
			"init_capital" : 100000,
		}
	},
	"sysfilter" : {
		"cls" : demo1_sysfilter.demo1_sysfilter,
		"opt" : { 'symbol' : 'QQQ', 'period' : 200, "algo" : "ALGO_1" },
	},
	"entryalgo" : 
	{
		"cls" : demo1_entry_algo.demo1_entry_algo,
		"opt" : {
			"pp" : { 
				'lperiod':252,
				'speriod':22,
			},
			"op" : { 
				'q_lowratio' : (0.85,1),
				'q_pvachgratio' : (0.5,1),
			},
		},
	},
	"exitalgo" : 
	{
		"cls" : demo1_exit_algo.demo1_exit_algo,
		"opt" : {
			"pp" : { 
				'period':60, 
				'multiple':20,
				'max_pct_risk':0.35,
			},
			"op" : { 
				'max_age':650,
			},
		},
	},
	"universe" : 
	{
		"cls" : index_universe.IndexUniverse,
		"opt" : {
			"indexname" : "NASDAQ 100",
			"date_range" : [str_to_dt('2000-01-01'),str_to_dt('2020-03-31')],
		}
	}
}

# --
# -- tests
# --
test_1 = {
	**index_specific_setup,
	"entryalgo/opt/op/q_pvachgratio/0" : [0.5, 0.6, 0.7, 0.8, 0.9],
}
test_2 = {
	**index_specific_setup,
	"simulator/opt/maxpos" : range(26,35,2),
}
test_3 = {
	**index_specific_setup,
	"exitalgo/opt/pp/max_pct_risk" : [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],
}
test_4 = {
	("universe/opt/indexname","sysfilter/opt/symbol") : 
	[ 
		("NASDAQ 100","QQQ"), 
		("Russell 1000","IWB"),
		("S&P 500","SPY"), 
	],
	"sysfilter/opt/period" : [ 10,20,50,100,200,300,400,500,600 ],
}
test_5 = {
	("universe/opt/indexname","sysfilter/opt/symbol") : 
	[ 
		("NASDAQ 100","QQQ"), 
		("Russell 1000","IWB"),
		("S&P 500","SPY"), 
	],
	"entryalgo/opt/op/q_pvachg/0" : [ 0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 ],
}
test_6 = {
	("universe/opt/indexname","sysfilter/opt/symbol") : 
	[ 
		#("NASDAQ 100","QQQ"), 
		#("Russell 1000","IWB"),
		("S&P 500","SPY"), 
	],
	"entryalgo/opt/op/q_lowratio" : [ 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95 ],
}
# --
# -- misc
# --
test_n = {
	("universe/opt/indexname","sysfilter/opt/symbol") : 
	[ 
		("NASDAQ 100","QQQ"), 
		("S&P 500","SPY"), 
		("Russell 1000","IWB"),
	],
	# "simulator/opt/maxpos" : range(5,51,5),
	# "sysfilter/opt/period" : range(50, 401, 50),
	# "exitalgo/opt/op/max_age" : range(300, 901, 50),
	# "exitalgo/opt/pp/period" : range(20, 101, 10),
	# "exitalgo/opt/pp/multiple" : range(0, 41, 5),
	# "entryalgo/opt/pp/low_ratio" : low_ratio_tuple_list_test_2_only(),
}
test_f_1 = {
	("entryalgo/opt/pp/low_ratio/0","entryalgo/opt/pp/low_ratio/1") : 
	[
		( round(n,1) , round(n+d,1) )
		for n in (0.0,1.0,2.0,3.0,4.0)
		for d in (0.5,1.0,2.0,3.0,5.0)
	]
}
