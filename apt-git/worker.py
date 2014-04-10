import threading
import Queue

class Worker(threading.Thread):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.queue = Queue.Queue()
	
	def run(self):
		while true:
			task = queue.get(true)
			task.execute()