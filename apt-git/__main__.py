#!/usr/bin/python
#PYTHON_ARGCOMPLETE_OK

import argparse
import httplib
import threading
import time
import Queue
from git import *
from datetime import datetime
import shutil
import os.path
import argcomplete

# Global parameters
VERSION = '0.1.1'
VERBOSE = False
TEMP_DIR = './.apt-git/'
INSTALL_DIR = os.environ['HOME'] + '/apt-git/'

sources = ('github.com',)

# Global functions

def weave(**args):
	thread = threading.Thread(**args)
	thread.daemon = True
	thread.start()
	return thread

def find(repository):
	for key, value in repo_dict.iteritems():   # iter on both keys and values
		if key.startswith(repository):
			res[key]=value

		return res


# Multiprocessable functions

# Check if the repository at source exists
def check_repository_address(source, repository, valid_repository_queue):
	# Check if https connection can be made
	addr = "https://"+source+"/"+repository+".git"
	if VERBOSE:
		print "Now checking for the existance of",addr+"."
	http = httplib.HTTPSConnection(source, 443)
	http.request("HEAD", "/"+repository)
	response = http.getresponse()

	if VERBOSE:
		print "Connecting to https://"+source+"/"+repository,", reponse status:",str(response.status)+"."
	
	if response.status==200:
		print "Valid repository found: ",addr
		valid_repository_queue.put(addr)

def pull_repository_data(addr, branch, repository_data_queue):
		print "Checking latest commit date for",addr,"on branch '",branch+"'."
		repo = Repo.clone_from(addr, './.apt-git/',commit='refs/heads/master')
		latest = repo.heads.master.commit.authored_date

		date = datetime.strftime(datetime.fromtimestamp(latest),'%Y-%m-%d')
		time = datetime.strftime(datetime.fromtimestamp(latest),'%H:%M:%S')
		if VERBOSE:
			print "Lastest commit was on",date,"at",time+"."
		repository_data_queue.put((latest*-1,(addr,branch))) # Smallest entry is the latest updated, so it's on top of the queue


# Multiprocessing helpers

def valid_repository_queue_watcher(valid_repository_queue, repository_data_queue):
	while(True):
		addr = valid_repository_queue.get(True)
		branch = 'master'
		weave(target=pull_repository_data, args=(addr, branch, repository_data_queue))

# Command functionalities

# Install new reposities
def install(repositories):
	valid_repository_queue = Queue.Queue()
	repository_data_queue = Queue.PriorityQueue()

	weave(target=valid_repository_queue_watcher, args=(valid_repository_queue, repository_data_queue))

	for repository in repositories:
			for source in sources:
				checker = weave(target=check_repository_address, args=(source, repository, valid_repository_queue))


  # Wait while the last checker thread is still alive
	while(checker.isAlive()):
		pass

	try:
		repository = repository_data_queue.get(True,8) # Wait for next repository for 8 seconds, else time out
	except Queue.Empty:
		print 'No valid repositories were found. (did you spell everything right?)'
		exit(0)

	# Pick the repository with the newest commit on the branch
	(latest,(addr,branch)) = repository
	print "The most up to date repository that was found is",addr+"."
	print "Installing the repository at ",addr,"to '",INSTALL_DIR+"'."

	if not(os.path.exists(INSTALL_DIR)):
		os.makedirs(INSTALL_DIR,0755)
	repository = Repo.clone_from(addr, INSTALL_DIR)
	repository.remotes.origin.pull(branch)

def remove(repositories):
	for repository in repositories:
			path = INSTALL_DIR + repository
			print "Checking if ",path,"exists."
			if os.path.exists(path):
				print "Removing repository",repository,"from your system."
			 	weave(target=shutil.rmtree, args=(path))


# Define and parse arguments

# Custom parsing action to generate new functionalities dynamically
class FunctionCallAction(argparse.Action):
	 def __call__(self, parser, namespace, values, option_string=None):
			 setattr(namespace, self.dest, globals()[values])

# Create parser
parser = argparse.ArgumentParser(
	description='Process some integers.',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
argcomplete.autocomplete(parser)

# Define arguments
parser.add_argument('-v','--verbose',dest='VERBOSE',action='store_true')
parser.add_argument('-V','--version',action='version',version=VERSION)

parser.add_argument('command',choices=('install','remove','update','upgrade'),action=FunctionCallAction,help='Select a command.')

parser.add_argument('arguments', metavar='args', type=str, nargs='+', help='Arguments to pass to the command.')

# Parse arguments
args = parser.parse_args()

# Set flags
VERBOSE = args.VERBOSE

# Create temp dir
if not(os.path.exists(TEMP_DIR)):
		os.makedirs(TEMP_DIR,0755)

# Apply chosen functionality to arguments
args.command(args.arguments)

# Clean up
if os.path.exists(TEMP_DIR):
	shutil.rmtree(TEMP_DIR)
