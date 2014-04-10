import threading
import Queue

class Task:
	def __init__(self,function,args):
		self.function = function
		self.args = args

	def execute(self):
		self.function(self.args)

class Worker(threading.Thread):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.queue = Queue.Queue()
	
	def run(self):
		while true:
			task = queue.get(true)
			task.execute()