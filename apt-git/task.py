import threading
import Queue

class Task:
	def __init__(self,function,args):
		self.function = function
		self.args = args

	def execute(self):
		self.function(self.args)