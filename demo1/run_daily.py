from jackutil.microfunc import str_to_dt,str_to_dt64,dt64_to_str
from jackutil.containerutil import projectContainer,containerChecksum
from backtest.tradesim_util import build_simulator,account_profit_summary
from pprint import pprint
import demo1_cfg as cfg
import sys
import datetime

def main(indexname,dtstr):
	# ----------------------------------------------------------------
	indexspec = {
		'r1000':cfg.r1000spec,
		's500':cfg.s500spec,
		'n100':cfg.n100spec,
	}[indexname]
	# ----------------------------------------------------------------
	enddt = str_to_dt(dtstr)
	startdt = enddt - datetime.timedelta(days=500)
	run_single_spec = {
		**indexspec,
		"universe/opt/date_range/0" : startdt,
		"universe/opt/date_range/1" : enddt,
	}
	print(run_single_spec)
	# ----------------------------------------------------------------
	(actions,rtcfg) = run_single(run_single_spec)
	print(containerChecksum(rtcfg))
	for action in actions:
		print("#" * 80)
		print('rundate',dt64_to_str(action['rundate']))
		print('sysfilter',action['sysfilter'])
		print('stageopen',action['stageopen'][1].tolist())
		print('stageclose',action['stageclose'])

def run_single(spec):
	rtcfg = projectContainer(cfg.basespec,spec)
	simulator = build_simulator(rtcfg)
	actions = simulator.runDailyAction(days=5)
	return ( actions, rtcfg )

# --
# -- ======================================
# --

if(__name__=="__main__"):
	main(*sys.argv[1:])
