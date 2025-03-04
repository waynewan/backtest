from setuptools import setup
setup(
	name='backtest',
	version='0.2.0.8.dev1',
	description='backtest library',
	url='#',
	author='#',
	author_email='#',
	license='Apache 2.0',
	packages=[
		'backtest',
		'backtest.abc'],
	package_dir={
		'backtest':'backtest',
		'backtest.abc':'abc'},
	zip_safe=False
)
