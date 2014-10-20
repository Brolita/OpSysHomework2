







ready = [(1,1),(1,2),(0,2),(0,1),(2,1),(2,2)]


all = []





for process in ready:
	i = 0								# start at 0
	#ordered insertion
	while True:							# loop up
		if i >= len(all):				# if were at the end
			all.append(process)			# insert and break
			break
		if process[0] < all[i][0]: # if were less then the one were looking at
			all.insert(i, process) #insert us infront of it
			break
		i+=1
		
		
print all