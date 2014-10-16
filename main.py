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
		self._starttime = None
		self._waittime = time.getTime()
		self._burstwaittime = 0
		self.arrived = False
		#self.arrivalTime
		#self.burstCount
		#self.burstMin
		#self.burstMax
		#self.interactive
		#self.IOmin
		#self.IOmax
		#self.running
		
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
		if "burstMin" not in processData:
			if debug: 
				print processId, "does not have a burstMin, defaulting to 200"
			processData["burstMin"] = 200
		self.burstCount = processData["burstCount"]
		self.burstMax = processData["burstMax"]
		self.burstMin = processData["burstMin"]
	
		self.burst = math.floor(self.burstMin + (self.burstMax - self.burstMin) * random.random())
		
		if "interactive" not in processData:
			if debug:
				print processId, "was not labeled interactive, defaulting to false"
			processData["interactive"] = False
			if self.processId is 0:
				processData["interactive"] = True
		self.interactive = processData["interactive"]
		self.running = not self.interactive
		if self.interactive:
			if "IOmax" not in processData:
				if debug: 
					print processId, "was labeled as interactive, but has no IOmax, defaulting to 3200"
				processData["IOmax"] = 3200
			if "IOmin" not in processData:
				if debug:
					print processId, "was labeled as interactive, but has no IOmin, defaulting to 100"
				processData["IOmin"] = 1200
			self.IOmax = processData["IOmax"]
			self.IOmin = processData["IOmin"]
		
		if self.arrived:
			print "[time 0ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time)"
			
	def isInteractive(self):
		return self.interactive
	
	def IOwait(self):
		self._starttime = time.getTime()
		self.burst = math.floor(self.IOmin + (self.IOmax - self.IOmin) * random.random())
		self.mode = False
		
	def IOstop(self):
		self.burst = 0
		self._starttime = None
		self.mode = None
		print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time)"
					
	def canIOstop(self):
		return self.mode is False and self.burst <= 0
	
	def start(self):
		self._starttime = time.getTime()
		if self._waittime is not None: # protect against initial condition
			self.waitTime += self._starttime - self._waittime 
			self._burstwaittime += self._starttime - self._waittime
		self.mode = True
	
	def preempt(self):
		self._waittime = time.getTime()
		self.mode = None
	
	def stop(self):
		print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "finished", "(turnaround time", str(time.getTime() - self._starttime) + "ms, wait time", str(self._burstwaittime) + "ms)"
		self._waittime = time.getTime()
		self._starttime = None
		self.mode = None
		self.burstCount -= 1
		self.burst = math.floor(self.burstMin + (self.burstMax - self.burstMin) * random.random())
		if self.burstCount is 0:
			self.running = False
			return
		if not self.interactive:
			print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time)"
	
	def step(self):
		if self.mode is not None:
			self.burst -= time.dt
	
	def isRunning(self):
		return (self.running or self.interactive)
	
	def isWaiting(self):
		if not self.arrived and time.getTime() > self.arrivalTime:
			self.arrived = True
			self._waittime = time.getTime()
			print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time)"
			return True
		return self._starttime is None and self.arrived and self.isRunning()
	
	def isBursting(self):
		return self._starttime is not None and self.mode
		
	def canStop(self):
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
						if process.isInteractive(): 	# if its intertactive
							process.IOwait()			# start IO
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
						if process.isInteractive(): 	# if its intertactive
							process.IOwait()			# start IO
						self.jobs.remove(process)		# remove process from jobs
						self.freeCores.append(process.core) # add free core
					elif debug:
						print process.burst, "time remaining on process", process.processId
				for process in self.processes:
					if process.canIOstop():
						process.IOstop()
				#if time.getTime() - 10 > globe:
					#for process in self.processes:
						#print process.processId, process.burst
					#globe = time.getTime()
				if len(self.jobs) == self.cores:		# if we have a full queue
					continue							# stop this loop
				'''
				new jobs
				'''	
				all = []								# ready a list of all jobs
				for process in self.processes:
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