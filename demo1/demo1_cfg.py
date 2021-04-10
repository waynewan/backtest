from jackutil.microfunc import str_to_dt
from jackutil.configuration import configuration
from backtest import tradesim_rotational,norgate_helper
from backtest import index_universe
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
n100spec,s500spec,r1000spec = configuration(basespec={},variations=index_specific_setup).all_variations()

test1 = {
	"entryalgo/opt/pp/lperiod" : range( 190, 215, 10 ),
	"entryalgo/opt/pp/speriod" : range(  90, 115, 10 ),
	"simulator/opt/maxpos" : range( 10, 35, 10 )
}

# --
# -- boiler plate
# -- "pp" -- bar loading postprocessor
# -- "op" -- object operating option
# --
basespec = {
	"simulator" : {
		"cls" : tradesim_rotational.Tradesim,
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
				'lperiod':200,
				'speriod':150,
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

