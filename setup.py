try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': 'GridPi',
	'author': 'Owen Edgerton',
	'url': 'https://github.com/ohowland/GridPi',
	'download_url': 'https://github.com/ohowland/GridPi',
	'author_email': 'ohowland@gmail.com',
	'version': '0.1',
	'install_requires': ['nose','pymodbus3'],
	'packages': ['NAME'],
	'scripts': [],
	'name': 'GridPi'
}

setup(**config)
