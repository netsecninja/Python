#Subnet script
#Determines last IP based on subnet mask and pings it.
#Those without a pingable device are listed on screen.
#
#Uses a CSV export from the HBSS Subnet Coverage Query
#Save as a csv
#csv contains the following columns:
#Subnet Name, Subnet Address, Subnet Mask, Covered
#
#Usage: subnet.py <filename with path>

#Imports
from sys import argv
from csv import reader
from ipaddress import ip_network
from subprocess import call, DEVNULL

#Variables
file = reader(open(argv[1], 'r'))

#Functions
def getLastIP(subnet, mask):
	return list(ip_network(subnet + "/" + mask, strict=False).hosts())[-1]

def ping(host):
	result = call("ping -n 1 " + host, stdout=DEVNULL, stderr=DEVNULL)
	return result
	
#Main
next(file) #skips header
print("Subnets not on network:")
for line in file:
	subnet = line[1]
	mask = line[2]
	ip = str(getLastIP(subnet, mask))
	check = ping(ip)
	if check == 0:
		continue
	else:
		print(subnet)
