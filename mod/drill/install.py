from dotinstall import util


def run():
    util.run_verbose(['pip', 'install', '.', '--upgrade', '--user'])
