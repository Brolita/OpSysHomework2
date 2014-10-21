Collaberators: 
	Aleksandr Han (RIN 661119383)
	Corey Byrne (RIN 661109135)
	Spencer Johnson (RIN 661129178)
	
Notes:
	There is a process class, a schedule class, and an analysis class
	options are set on line 600 (the very end of main.py)
	mode 0 is SJF non-preemptive
	mode 1 is SJF preemptive
	mode 2 is Round Robin
	mode 3 is Aging algorithm
	
Assumptions:
	We assumed context switching only need to be done during process preempt
	it would have been fairly simple to always do context switch if this was
	not the case
	
	We assumed all processes need analysis preformed, and thus all processes
	have analysis done on them. It would have been easy to not print interactive
	processes