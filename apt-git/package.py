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

		self.installed = os.path.exists(os.path.join(self.install_dir,'.git'))

		if self.installed:
			self.repository = Repo(self.install_dir)

	def install(self):
		# Create temp dir
		if not self.installed:
			os.makedirs(self.install_dir, 0775)

		print "Installing the repository at ", self.url, "to ", self.install_dir, "."

		self.repository = Repo.init(self.install_dir)
		if not self.repository.remotes:
			self.repository.create_remote(self.source, self.url)
		
		# Get the most recent data
		self.update()
		#self.upgrade()

	def install_async(self):
		installer = threading.Thread(target=self.install)
		installer.start()
		return installer


	def update(self):
		print "Checking active branch."
		self.branch = self.repository.active_branch.name

		print "Fetching latest data from remotes"
		for remote in self.repository.remotes:
			print "Checking latest commit date for remote",remote.name,"on branch",self.branch+"."

			# Check if remote has the requested branch
			try:
				remote.fetch("refs/heads/"+self.branch+":refs/remotes/"+remote.name+"/"+self.branch)
			except:
				print "The branch does not exist on remote",remote.name+"."
				continue

			latest_commit_at = remote.refs[self.branch].commit.authored_date

			date = datetime.strftime(datetime.fromtimestamp(latest_commit_at),'%Y-%m-%d')
			time = datetime.strftime(datetime.fromtimestamp(latest_commit_at),'%H:%M:%S')
			print "Lastest commit for remote",remote.name," was on",date,"at",time+"."
			self.updated.put((latest_commit_at*-1,remote)) # Smallest entry is the latest updated, so it's on top of the queue
	
	def update_async(self):
		updater = threading.Thread(target=self.update)
		updater.start()
		return updater

	def upgrade(self):
		return
		#remote.pull(self.branch)

	def upgrade_async(self):
		upgrader = threading.Thread(target=self.upgrade)
		upgrader.start()
		return upgrader

	def remove(self):
		if not self.installed: 
			print "Repository",self.name,"is not installed."
			return
		shutil.rmtree(os.path.dirname(self.install_dir))

	def remove_async(self):
		remover = threading.Thread(target=self.remove)
		remover.start()
		return remover