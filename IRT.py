# Incident Response Tool (IRT)
# Coded by Jeremiah Bess because he's lazy
# "Progress is made by lazy men looking for easier ways to do things." - Robert A. Heinlein

# Imports
import os, time, datetime, fnmatch

# Variables
eventdate = ""
eventtime = ""
eventip = ""
comp = ""
macs = []
path = r"\\SERVERNAME\DRIVELETTER$\dhcp\logs"
inits = ""

# Functions
def Menu():
	print("Incident Response Tool v0.6") # Print header
	print("""
1. Computer from IP
2. MACs from Computer
3. DHCP Block
4. AD Block

0. Quit
""")
	menu = input("Please choose an option: ") # Menu choices made here
	if menu == "1": # IP -> Comp
		ip2comp()
	elif menu == "2": # Comp -> MACs
		comp2mac()
	elif menu == "3": # DHCP Block
		dhcpblock()
	elif menu == "4": # AD Block
		adblock()
	elif menu == "0":
		exit()
	else:
		print("Function not working yet. Returning to Main Menu.")
		time.sleep(2)
		os.system ('cls') # Clears screen for clean look
		
def ip2comp():
	global eventdate
	global eventtime
	global eventip
	global comp
	global path
	
	while True: # Get Date
		ask = input("Enter event date in YYYYMMDD format or 0 for today " + "[" + eventdate + "]:")
		if ask != "0" and len(eventdate) == 0 and len(ask) != 8:
			print("Invalid date format.")
		elif not ask == "":
			eventdate = ask
			break
		else:
			break
			
	while True: # Get Time
		ask = input("Enter event time in HHMM (local, 24 hour) format " + "[" + eventtime + "]:")
		if ask == "" and eventtime == "":
			print("Invalid time.")
		elif not ask == "":
			eventtime = ask
			break
		else:
			break
			
	while True: # Get IP Address
		ask = input("Enter IP address " + "[" + eventip + "]:")
		if ask == "" and eventip == "":
			print("Invalid IP address.")
		elif not ask == "":
			eventip = ask
			break
		else:
			break
			
	# Validates and manipulates eventdate
	today = datetime.date.today()
	if eventdate == "" or eventdate == "0" or eventdate == today.strftime("%Y%m%d"): # Run search on today's log
		if eventdate == "" or eventdate == "0":
			eventdate = today.strftime("%Y%m%d") # Set variable to today
		pattern = "DhcpSrvLog-"+today.strftime("%a")+".log"
	else:
		eventdate = eventdate + "-*" # Add * as a wildcard to search
		pattern = eventdate
		
	# Validates and manipulates eventtime
	eventtime = str(eventtime) # convert to string
	h1, h2, m1, m2 = eventtime # separate each character
	eventtime = h1+h2+":"+m1+m2 # recombine to add the colon
	
	# Validates and manipulates eventip
	eventip = eventip + ","
    
	# Finds file name based on date entered
	for file in os.listdir(path):
		if fnmatch.fnmatch(file, pattern):
			break 

	# Searched file for IP
	logentries = []
	try:
		log = open(path + "\\" + file, "r")
	except PermissionError:
		os.system ('cls') # Clears screen for clean look
		print("*"*36 + " Error " + "*"*36)
		print("Your account does not have permissions to the DHCP server")
		print("*"*79)
		print("")
		return
	for line in log:
		if eventip in line:
			logentries.append(line)
	log.close()

	# Parse entries found
	if len(logentries)== 0:
		comp = ""
	else:
		for entry in logentries:
			if entry.split(",")[2].rsplit(":",1)[0] < eventtime: # If the date is less than the event date
					comp = entry # Store the entry in 'last' variable
			else: # Stop processing entries
				break
		if comp != "":
			comp = comp.split(",")[5].split(".")[0] #Strips out computer name in line
			comp = comp.upper() # Capitalize
		
	# Format and display results
	eventdate = eventdate.rstrip("-*")
	eventtime = eventtime.replace(":","")
	eventip = eventip.rstrip(",")
	os.system ('cls') # Clears screen for clean look
	print("*"*29 + " Last Search Results " + "*"*29)
	print("Comp: " + comp)
	print("IP: " + eventip)
	print("Date: " + eventdate)
	print("Time: " + eventtime)
	print("*"*79)
	print("")

def comp2mac():
	global comp
	global path
	global macs
	
	while True: # Get Date
		ask = input("Enter computer name [" + comp + "]:")
		if len(ask) == 0 and len(comp) == 0:
			print("Invalid computer name.")
		elif not ask == "":
			comp = ask
			break
		else:
			break
	
	comp = comp.upper() # Capitalize
	today = datetime.date.today() # Get today's date
	date_range = []
	file_list = []
	mac_list = []
	
	for x in range(1, 8): # Calculate range to 7 days back
		date_range.append(today - datetime.timedelta(days=x))
		
	for day in date_range: # Find files matching name range
		pattern = str(day.strftime("%Y%m%d")) + "-*" # Add * as a wildcard to search
		for file in os.listdir(path): # Locate files according to pattern
			if fnmatch.fnmatch(file, pattern):
				file_list.append(file)
	
	for file in file_list: # Search file for MAC, append to list
		try:
			log = open(path + "\\" + file, "r")
		except PermissionError:
			os.system ('cls') # Clears screen for clean look
			print("*"*36 + " Error " + "*"*36)
			print("Your account does not have permissions to the DHCP server")
			print("*"*79)
			print("")
			return
		for line in log:
			# Try fileinput and csv
			if line[0:2] == "11":
				try:
					temp = line.split(",")
					if temp[5].split(".")[0].upper() == comp and temp[6] not in mac_list:
						mac_list.append(temp[6])
				except IndexError:
					continue
		log.close()
	
	if len(mac_list) == 0:
		macs = [] # If nothing found, blank global list
	else:
		macs = mac_list
	
	os.system ('cls') # Clears screen for clean look
	print("*"*29 + " Last Search Results " + "*"*29)
	print("Comp: " + comp)
	print("MACs: ", end="")
	for mac in macs:
		print(mac, end=" ")
	print("\r")
	print("*"*79)
	print("")

def dhcpblock():
	global inits
	
	if comp == "" or macs == []:
		print("No stored computer name or MACs. Try another function first.")
		time.sleep(3)
		os.system ('cls') # Clears screen for clean look
		return
	
	while True:
		ask = input("Enter your initials [" + inits + "]:")
		if len(ask) == 0: # If empty response and nothing stored
			if len(inits) == 0:
				print("Invalid initials.")
			else:
				break
		elif len(ask) < 2 or len(ask) > 3 or ask.isalpha() == False:
				print("Invalid initials. Check")
		elif not ask == "": # All good, set it
			inits = ask.upper()
			break
		else: # Use stored
			break
	
	today = datetime.date.today()
	
	os.system ('cls') # Clears screen for clean look
	print("*"*28 + " Copy/Paste text below " + "*"*28)
	for mac in macs:
		print(mac)
	print("Security - " + comp, today.strftime("%d %b %y"), inits)
	print("*"*79)
	print("")

def adblock():
	global inits
	
	if comp == "":
		print("No stored computer name. Try another function first.")
		time.sleep(3)
		os.system ('cls') # Clears screen for clean look
		return
	
	while True:
		ask = input("Enter your initials [" + inits + "]:")
		if len(ask) == 0: # If empty response and nothing stored
			if len(inits) == 0:
				print("Invalid initials.")
			else:
				break
		elif len(ask) < 2 or len(ask) > 3 or ask.isalpha() == False:
				print("Invalid initials. Check")
		elif not ask == "": # All good, set it
			inits = ask.upper()
			break
		else: # Use stored
			break
	
	today = datetime.date.today()
	
	os.system ('cls') # Clears screen for clean look
	print("*"*28 + " Copy/Paste text below " + "*"*28)
	print(comp)
	print("Disabled for security incident " + today.strftime("%d %b %y"), inits)
	print("*"*79)
	print("")

# Main program
os.system ('cls') # Clears screen for clean look
while True:
	Menu()
