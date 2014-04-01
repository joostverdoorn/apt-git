from git import *
from datetime import datetime

import shutil
import os.path
import Queue
import threading



class Package: 

	source = "github.com"

	def __init__(self, name, main_dir="/tmp", branch="master"):
		self.name = name

		self.install_dir = os.path.join(main_dir, self.name)
		self.branch = branch
		self.updated = Queue.PriorityQueue()
		


		self.url = "https://"+os.path.join(self.source,self.name)

		self.installed = os.path.exists(self.install_dir)
		print self.installed

	def install(self):
		# Create temp dir
		if not self.installed:
			os.makedirs(self.install_dir, 0775)

		print "The most up to date repository that was found is ", self.url, "."
		print "Installing the repository at ", self.url, "to ", self.install_dir, "."

		self.repository = Repo.init(self.install_dir)
		self.repository.create_remote(self.source, self.url)
		
		# Get the most recent data
		#self.update()
		#self.upgrade()

	def install_async(self):
		installer = threading.Thread(target=self.install)
		installer.start()
		return installer


	def update(self):
		print "Checking latest commit date for",self.url+"."
		remote = self.repository.refs[self.branch]
		remote.fetch()
		latest_commit_at = self.repository[self.branch].commit.authord_date


		date = datetime.strftime(datetime.fromtimestamp(latest),'%Y-%m-%d')
		time = datetime.strftime(datetime.fromtimestamp(latest),'%H:%M:%S')
		if VERBOSE:
			print "Lastest commit was on",date,"at",time+"."
		self.updated.put((latest*-1,(addr,branch))) # Smallest entry is the latest updated, so it's on top of the queue

	def upgrade(self):
		self.repository.remotes.origin.pull(self.branch)
		
	def remove(self):
		if not self.installed: 
			print "Target directory not found."
			return
		shutil.rmtree(os.path.dirname(self.install_dir))


	def remove_async(self):
		remover = threading.Thread(target=self.remove)
		remover.start()
		return remover


	def addSource(self, name, url):
		pass