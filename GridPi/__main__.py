from GridPi.lib import gridpi
from configparser import ConfigParser
from pathlib import Path
import logging

def main(*args, **kwargs):

    print('-----------------------')
    print('Booting GridPi v0.1')
    print('-----------------------')

    if kwargs.get('-d'):
        print('# Logging warnings to console')
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

    if kwargs.get('-c', 0):
        print('# Loading custom bootstrap configuration')
        bootstrap_path = Path.cwd().joinpath(kwargs['-c'])
    else:
        bootstrap_path = Path.cwd()
        while bootstrap_path.parent.stem == 'GridPi':
            bootstrap_path = bootstrap_path.parent
        bootstrap_path = bootstrap_path.joinpath('GridPi', 'config', 'bootstrap.ini')
        print('# Loading bootstrap configuration: {}'.format(bootstrap_path.as_posix()))

    bootstrap_parser = ConfigParser()
    bootstrap_parser.read(bootstrap_path.as_posix())

    print('# Launching main()')
    print('-----------------------')
    gridpi.main(bootstrap=bootstrap_parser)

    print('-----------------------')
    print('Shutdown Complete')
    print('-----------------------')

if __name__ == '__main__':
    main()
