import json
import datetime
import random
import math

debug = False

class timeGetter:
	def __init__(self):
		self.startTime = datetime.datetime.now()
		self.steptime = 0
		self.lasttime = datetime.datetime.now()
		self.dt = 0
		
	def getTime(self):
		return self.steptime
	
	def step(self):
		currentTime = datetime.datetime.now()
		delta = currentTime - self.startTime
		self.dt = (currentTime - self.lasttime).total_seconds()*1000
		if debug:
			while (currentTime - self.lasttime).total_seconds() < .1:
				currentTime = datetime.datetime.now()
				delta = currentTime - self.startTime
			self.steptime = delta.total_seconds() * 100
			self.lasttime = currentTime
			return
		self.steptime = delta.total_seconds()*1000
		self.lasttime = currentTime
			
time = timeGetter()		

class process:
	def __init__(self, processData, processId):
		self.processId = processId
		self.core = -1
		self.waitTime = 0
		self.mode = None
		self.priority = 0
		self._startTime = None
		self._waitTime = time.getTime()
		self._burstwaittime = 0
		self.arrived = False
		self.lastWaitTime = 0;
		self.contextSwitch = False
		self.preempted = False
		#self.arrivalTime
		#self.burstCount
		#self.burstMin
		#self.burstMax
		#self.interactive
		#self.IOmin
		#self.IOmax
		#self.running
		
		if "interactive" not in processData:
			if debug:
				print processId, "was not labeled interactive, defaulting to false"
			processData["interactive"] = True if random.random() < .8 else False;
		self.interactive = processData["interactive"]
		
		if "arrivalTime" not in processData: 
			if debug:
				print processId, "does not have a arrivalTime, defaulting to 0"
			processData["arrivalTime"] = 200
		self.arrivalTime = processData["arrivalTime"]
		if self.arrivalTime == 0:
			self.arrived = True
	
		if "burstCount" not in processData:
			if debug:
				print processId, "does not have a burstCount, defaulting to 8"
			processData["burstCount"] = 8
		if "burstMax" not in processData:
			if debug:
				print processId, "does not have a burstMax, defaulting to 3000"
			processData["burstMax"] = 3000
			if self.interactive:
				processData["burstMax"] = 200
		if "burstMin" not in processData:
			if debug: 
				print processId, "does not have a burstMin, defaulting to 200"
			processData["burstMin"] = 200
			if self.interactive:
				processData["burstMin"] = 20
		self.burstCount = processData["burstCount"]
		self.burstMax = processData["burstMax"]
		self.burstMin = processData["burstMin"]
	
		self.burst = math.floor(self.burstMin + (self.burstMax - self.burstMin) * random.random())
	
		self.running = not self.interactive
		if "IOmax" not in processData:
			if debug: 
				print processId, "was labeled as interactive, but has no IOmax, defaulting to 3200"
			processData["IOmax"] = 3200
			if self.interactive:
				processData["IOmax"] = 4500
		if "IOmin" not in processData:
			if debug:
				print processId, "was labeled as interactive, but has no IOmin, defaulting to 100"
			processData["IOmin"] = 1200
			if self.interactive:
				processData["IOmin"] = 1000
		self.IOmax = processData["IOmax"]
		self.IOmin = processData["IOmin"]
		
		if self.arrived:
			print "[time 0ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time)"
			
	def isInteractive(self):
		return self.interactive
	
	def IOwait(self):
		self._startTime = time.getTime()
		self.burst = math.floor(self.IOmin + (self.IOmax - self.IOmin) * random.random())
		self.mode = False
			
	def IOstop(self):
		self.burst = math.floor(self.burstMin + (self.burstMax - self.burstMin) * random.random())
		self._startTime = None
		self.mode = None
		print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time)"
					
	def canIOstop(self):
		return self.mode is False and time.getTime() - self.burst > self._startTime
	
	def start(self):
		self._startTime = time.getTime()
		if self._waitTime is not None: # protect against initial condition
			self.waitTime += self._startTime - self._waitTime 
			self._burstwaittime += self._startTime - self._waitTime
		self.mode = True
	
	def preempt(self):
		self.contextSwitch = True
		self._waitTime = time.getTime()
		self.mode = None
		self.preempted = True
	
	def stop(self):
		print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "finished", "(turnaround time", str(time.getTime() - self._startTime) + "ms, wait time", str(self._burstwaittime) + "ms)"
		self._waitTime = time.getTime()
		self._startTime = None
		self.mode = None
		self.burstCount -= 1
		self.burst = math.floor(self.burstMin + (self.burstMax - self.burstMin) * random.random())
		self.contextSwitch = True
		if self.burstCount is 0:
			self.running = False
		
	def runningTime(self):
		return time.getTime() - self._startTime
	
	def waitingTime(self):
		self.lastWaitTime = time.getTime() - self._waitTime
		return self.lastWaitTime
	
	def waitIncremented(self):
		self.lastWaitTime-=1200
	
	def step(self):
		if self.preempted:
			self.preempted = False
			self._startTime = time.getTime()
		elif self.mode is not None:
			self.burst -= time.dt
			
	def isRunning(self):
		return (self.running or self.interactive)
	
	def isWaiting(self):
		if not self.arrived and time.getTime() > self.arrivalTime:
			self.arrived = True
			self._waitTime = time.getTime()
			print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time)"
			return True
		return self._startTime is None and self.arrived and self.isRunning() and not self.preempt and not self.contextSwitch
	
	def isBursting(self):
		return self._startTime is not None and self.mode
		
	def canStop(self):
		if self.contextSwitch: 
			self.contextSwitch = False
			self._waitTime = time.getTime()
		return self.isBursting() and self.burst <= 0
		
	def timeLeft(self):    # note, only can be called is canStart is false
		return self.burst
	 
	
class scheduler:
	def __init__(self, scheduleData):
		self.jobs = []
		self.freeCores = []
		if "mode" not in scheduleData:
			if debug:
				print "Mode not listed in data, defaulting to 0 (SJF non-preemtive)"
			scheduleData["mode"] = 0
		self.mode = scheduleData["mode"]
		if "cores" not in scheduleData:
			if debug:
				print "Cores not listed in data, defauling to 4 cores"
			scheduleData["cores"] = 4
		self.cores = scheduleData["cores"]
		self.freeCores = range(self.cores)
		if self.mode == 2:
			if "timeSlice" not in scheduleData:
				if debug:
					print "TimeSlice not listed in data, defaulting to 100ms"
				scheduleData["timeSlice"] = 100
			self.timeSlice = scheduleData["timeSlice"]
		self.processes = []
		if "processes" not in scheduleData:
			if debug:
				print "No processes supplied, making 5 defaults"
			for i in range(5):
				self.processes.append(process({}, i))
		else:
			for i in range(len(scheduleData["processes"])):
				self.processes.append(process(scheduleData["processes"][i], i))
		
		self.main()
		
	def main(self):
		finished = False
		globe = 0
		
		
		
		
		
		
		if self.mode is 3: # BULLSHIT
			ready = []	
			while not finished:
				time.step()
				if debug:
					print "starting step," , len(self.jobs) , "jobs"
				'''
				current jobs
				'''
				for process in self.jobs:
					process.step()						# step the job
					if process.canStop(): 				# job can stop
						if debug:
							print "stopping process", process.processId
						process.stop()    				# stop the job
						if process.isRunning():
							process.IOwait()			# start IO
						self.jobs.remove(process)		# remove process from jobs
						self.freeCores.append(process.core) # add free core
						ready.remove(process)
					elif debug:
						print process.burst, "time remaining on process", process.processId
						
						
				for process in self.processes:
					if process.waitingTime() > 1200:
						process.waitIncremented()
					if process.isWaiting() and process not in ready:
						process.priority = math.floor(random.random()*5)
						if process.isRunning():
							ready.append(process)
					elif process.canIOstop() and process not in ready:
						process.priority = math.floor(random.random()*5)
						process.IOstop()
						if process.isRunning():
							ready.append(process)
						
						
				if len(self.jobs) == self.cores:		# if we have a full queue
					continue							# stop this loop
					
				all = []
				
				for process in self.processes:
					i = 0								# start at 0
					#ordered insertion
					while True:							# loop up
						if i >= len(all):				# if were at the end
							all.append(process)			# insert and break
							break
						if debug:
							print "loop", i, "checking priority", process.priority, "against", all[i].priority
						if process.priority < all[i].priority: # if were less then the one were looking at
							all.insert(i, process) #insert us infront of it
							break
						i+=1
				
				for i in range(len(all)):				# add all the new free cores
					if all[i] in self.jobs and i >= self.cores - 1 and len(all) > self.cores: # for processes that no longer quailify 
						print " ___ PREEMPT ___ "
						all[i].preempt()				# preempt the process
						self.jobs.remove(all[i])
						self.freeCores.append(all[i].core) # add the core we just freed					
				

				
				

	
				ready = all
							
				for process in ready:
				
					if len(self.jobs) == self.cores:	# when we've filled up the queue
						break							# stop
					if debug:
						print "process", process.processId, "being added"
					if process not in self.jobs:
						process.start()						# otherwise start this job
						self.jobs.append(process)			# and add it to the job list
						process.core = self.freeCores.pop(0)# add it to a free core
						print "[time " + str(time.getTime()) + "ms]", ("Interactive" if process.interactive else "CPU-bound"), "process ID", process.processId, "starting on core", process.core + 1
				'''
				check for end condition
				'''
				finished = True							# assume were done
				for process in self.processes:			# for each process
					finished = finished and not process.running # ask if they're done
		
		
		

		
		
		
		
		
		
		
		#self.mode = 2
		if self.mode is 2: # RR
			print "Round Robin Started"
			ready = []	
			#print self.freeCores
			tempTime = self.timeSlice							# ready a list of ready job
			while not finished:
				time.step()
				if debug:
					print "starting step," , len(self.jobs) , "jobs"
				'''
				current jobs
				'''
				for process in self.jobs:
					process.step()						# step the job
					if process.canStop(): 				# job can stop
						if debug:
							print "stopping process", process.processId
						process.stop()    				# stop the job
						if process.isRunning():
							process.IOwait()				# start IO
						self.jobs.remove(process)		# remove process from jobs
						
						self.freeCores.append(process.core) # add free core
						ready.remove(process)
					elif process.isBursting() and process.runningTime() > tempTime and len(ready) > self.cores:
						print self.cores
						print " ___ PREEMPT ___ ",process.processId ,process.burst
						process.preempt()				# preempt the process
						self.jobs.remove(process)
						self.freeCores.append(process.core) # add the core we just freed					
						
						
						ready.remove(process)
						ready.append(process)
					elif debug:
						print process.burst, "time remaining on process", process.processId
						
						
				for process in self.processes:
					if process.isWaiting() and process not in ready:
						ready.append(process)
					elif process.canIOstop() and process not in ready:
						process.IOstop()
						ready.append(process)
						
						
				if len(self.jobs) == self.cores:		# if we have a full queue
					continue							# stop this loop
					
				
	
							
							
				for process in ready:
				
					if len(self.jobs) == self.cores:	# when we've filled up the queue
						break							# stop
					if debug:
						print "process", process.processId, "being added"
					if process not in self.jobs:
						process.start()						# otherwise start this job
						self.jobs.append(process)			# and add it to the job list
						process.core = self.freeCores.pop(0)# add it to a free core
						print "[time " + str(time.getTime()) + "ms]", ("Interactive" if process.interactive else "CPU-bound"), "process ID", process.processId, "starting on core", process.core + 1
				'''
				check for end condition
				'''
				finished = True							# assume were done
				for process in self.processes:			# for each process
					finished = finished and not process.running # ask if they're done
		
		

		
		
		
		if self.mode is 1: # SJF non-preemptive
			while not finished:
				time.step()
				if debug:
					print "starting step," , len(self.jobs) , "jobs"
				'''
				current jobs
				'''
				for process in self.jobs:
					process.step()						# step the job
					if process.canStop(): 				# job can stop
						if debug:
							print "stopping process", process.processId
						process.stop()    				# stop the job
						process.IOwait()				# start IO
						self.jobs.remove(process)		# remove process from jobs
						self.freeCores.append(process.core) # add free core
					elif debug:
						print process.burst, "time remaining on process", process.processId
				for process in self.processes:
					if process.canIOstop():
						process.IOstop()
				if len(self.jobs) == self.cores:		# if we have a full queue
					continue							# stop this loop
				'''
				new jobs
				'''
				ready = []								# ready a list of ready job
				for process in self.processes:
					if process.isWaiting():				# if the job can start
						if debug:						
							print "process", process.processId, "ready to begin"
						i = 0							# start at 0
						#ordered insertion
						while True:						# loop up
							if i >= len(ready):			# if were at the end
								ready.append(process)	# insert and break
								break
							if debug:
								print "loop", i, "checking burst", process.burst, "against", ready[i].burst
							if process.burst < ready[i].burst: # if were less then the one were looking at
								ready.insert(i, process) #insert us infront of it
								break
							i+=1
				for process in ready:
					if len(self.jobs) == self.cores:	# when we've filled up the queue
						break							# stop
					if debug:
						print "process", process.processId, "being added"
					process.start()						# otherwise start this job
					self.jobs.append(process)			# and add it to the job list
					process.core = self.freeCores.pop(0)# add it to a free core
					print "[time " + str(time.getTime()) + "ms]", ("Interactive" if process.interactive else "CPU-bound"), "process ID", process.processId, "starting on core", process.core + 1
				'''
				check for end condition
				'''
				finished = True							# assume were done
				for process in self.processes:			# for each process
					finished = finished and not process.running # ask if they're done
		
		if self.mode is 0: # SJF preemptive
			while not finished:
				time.step()
				if debug:
					print "starting step," , len(self.jobs) , "jobs"
				'''
				current jobs
				'''
				for process in self.jobs:
					process.step()						# step the job
					
					if process.canStop(): 				# job can stop
						if debug:
							print "stopping process", process.processId
						process.stop()    				# stop the job
						process.IOwait()				# start IO
						self.jobs.remove(process)		# remove process from jobs
						self.freeCores.append(process.core) # add free core
					elif debug:
						print process.burst, "time remaining on process", process.processId
				for process in self.processes:
					if process.canIOstop():
						process.IOstop()
				if len(self.jobs) == self.cores:		# if we have a full queue
					continue							# stop this loop
				'''
				new jobs
				'''	
				
				all = []								# ready a list of all jobs
				for process in self.processes:
					if not process.isRunning() and not process.isWaiting():
						continue
					i = 0								# start at 0
					#ordered insertion
					while True:							# loop up
						if i >= len(all):				# if were at the end
							all.append(process)			# insert and break
							break
						if debug:
							print "loop", i, "checking burst", process.burst, "against", all[i].burst
						if process.burst < all[i].burst: # if were less then the one were looking at
							all.insert(i, process) #insert us infront of it
							break
						i+=1
				for i in range(len(all)):				# add all the new free cores
					if all[i] in self.jobs and i >= self.cores - 1: # for processes that no longer quailify 
						print " ___ PREEMPT ___ "
						all[i].preempt()				# preempt the process
						self.jobs.remove(all[i])
						self.freeCores.append(all[i].core) # add the core we just freed							
				for process in all:
					if len(self.jobs) == self.cores:	# when we've filled up the queue
						break							# stop
					if process in self.jobs:			# if this job is already running
						continue						# continue
					if debug:
						print "process", process.processId, "being added"
					process.start()						# otherwise start this job
					self.jobs.append(process)			# and add it to the job list
					process.core = self.freeCores.pop(0)# add it to a free core
					print "[time " + str(time.getTime()) + "ms]", ("Interactive" if process.interactive else "CPU-bound"), "process ID", process.processId, "starting on core", process.core + 1
				'''
				check for end condition
				'''
				finished = True							# assume were done
				for process in self.processes:			# for each process
					finished = finished and not process.running # ask if they're done
		
scheduler({})
