from jackutil.microfunc import str_to_dt,str_to_dt64
from jackutil.containerutil import projectContainer,containerChecksum
from backtest.tradesim_util import build_simulator,account_profit_summary
from pprint import pprint
import demo1_cfg as cfg
import sys

def main(indexname,dtstr):
	# ----------------------------------------------------------------
	indexspec = {
		'r1000':cfg.r1000spec,
		's500':cfg.s500spec,
		'n100':cfg.n100spec,
	}[indexname]
	# ----------------------------------------------------------------
	run_single_spec = {
		**indexspec,
		"universe/opt/date_range/0" : str_to_dt('2020-03-19'),
		"universe/opt/date_range/1" : str_to_dt('2021-04-19'),
	}
	# ----------------------------------------------------------------
	(buylist,rtcfg) = run_single(run_single_spec,str_to_dt64(dtstr))
	print(containerChecksum(rtcfg))
	pprint(buylist)

def run_single(spec,dt64):
	rtcfg = projectContainer(cfg.basespec,spec)
	return ( runDailyBuylist(rtcfg, dt64), rtcfg )

def runDailyBuylist(rtcfg, dt64):
	simulator = build_simulator(rtcfg)
	return simulator.runDailyBuylist(dt64)

# --
# -- ======================================
# --

if(__name__=="__main__"):
	main(*sys.argv[1:])
