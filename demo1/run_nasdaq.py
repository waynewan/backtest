from jackutil.containerutil import projectContainer,containerChecksum
from backtest.tradesim_util import build_simulator,account_profit_summary
import pprint

def main():
	# -----------------------------------------------------------------------------
	import demo1_cfg as cfg
	# -----------------------------------------------------------------------------
	# --
	# -- run single without cache
	# --
	rtcfg = projectContainer(cfg.basespec,cfg.n100spec)
	# rtcfg = projectContainer(cfg.basespec,cfg.s500spec)
	# --
	(account,d0,univers,simulator) = runBacktest(rtcfg=rtcfg)
	print(containerChecksum(rtcfg))
	print(account_profit_summary(account))

def runBacktest(rtcfg):
	simulator = build_simulator(rtcfg)
	(account,d0,universe) = simulator.runBacktest()
	return (account,d0,universe,simulator)

# --
# -- ======================================
# --

print(__name__)
if(__name__=="__main__"):
	main()
