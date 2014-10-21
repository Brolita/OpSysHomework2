class Analysis:
	#should take in as parameters things like wait time, burst time etc
	def __init__(self, _turnAround, _waitTime, _processId, _numOfContextSwitches):
		self.turnAround = _turnAround
		self.waitTime = _waitTime
		self.processId = _processId
		
		print str(self.turnAround - self.waitTime), str(self.turnAround + _numOfContextSwitches * 2)
		self.avgCPUutil = ((self.turnAround - self.waitTime) * 1.0) / ((self.turnAround) + _numOfContextSwitches * 2)
		#all of the necessary statistics should be calculated in the init
		
	#calculates the turn around time
	def CalculateTurnAround(self):
		pass
	
	#there will be more stuff here soon
		
	