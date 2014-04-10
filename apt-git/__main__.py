#!/usr/bin/python
#PYTHON_ARGCOMPLETE_OK

import argparse
import argcomplete
import os

# apt-git
from package import Package

# Global parameters
VERSION = '0.1.2'
VERBOSE = False
MAIN_DIR = os.environ['HOME'] + '/apt-git/'

def install(packages):
	installers = list()

	for package in packages:
		installer = package.install_async()
		installers.append(installer)

	# Wait untill all installers are done
	for installer in installers:
		installer.join()

def remove(packages):
	removers = list()

	for package in packages:
		remover = package.remove_async()
		removers.append(remover)

	# Wait untill all removers are done
	for remover in removers:
		remover.join()

def update(packages):
	updaters = list()

	for package in packages:
		updater = package.update_async()
		updaters.append(updater)

	# Wait untill all removers are done
	for updater in updaters:
		updater.join()

def upgrade(packages):
	upgraders = list()

	for package in packages:
		upgrader = package.upgrade_async()
		upgraders.append(upgrader)

	# Wait untill all removers are done
	for upgrader in upgraders:
		upgrader.join()

# Define and parse arguments

# Custom parsing action to generate new functionalities dynamically
class FunctionCallAction(argparse.Action):
	 def __call__(self, parser, namespace, value, option_string=None):
			 setattr(namespace, self.dest, globals()[value])

class PackageMapAction(argparse.Action):
	 def __call__(self, parser, namespace, package_names, option_string=None):
	 	packages = list()
	 	for package_name in package_names:
			packages.append(Package(package_name, main_dir=MAIN_DIR))
		setattr(namespace, self.dest, packages)

# Create parser
parser = argparse.ArgumentParser(
	description='Process some integers.',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
argcomplete.autocomplete(parser)

# Define arguments
parser.add_argument('-v','--verbose',dest='VERBOSE',action='store_true')
parser.add_argument('-V','--version',action='version',version=VERSION)
parser.add_argument('-T','--target-dir',dest='MAIN_DIR',action='store')
parser.add_argument('command',choices=('install','remove','update','upgrade'),action=FunctionCallAction,help='Select a command.')
parser.add_argument('arguments', metavar='args', type=str, action=PackageMapAction, nargs='+', help='Arguments to pass to the command.')

# Parse arguments
args = parser.parse_args()

# Set flags
VERBOSE = args.VERBOSE
MAIN_DIR = args.MAIN_DIR

# Apply chosen functionality to arguments
args.command(args.arguments)