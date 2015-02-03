#imports
import socket, time

#variables
host = '10.1.0.2'
port = 1337

#functions
def knock(host, port): #connects to main port to get list of other ports to knock on
	s = socket.socket()
	s.connect((host,port))
	list = s.recv(1024).lstrip('[').rstrip(']\n').split(', ')
	print list
	s.close()
	return list

def rapping(host,raps): #connects to each port given from the main port
	for rap in raps:
		time.sleep(1)
		s = socket.socket()
		print "Port "+rap+"-->",
		try:
			s.connect((host, int(rap)))
			print s.recv(1024)
		except socket.error:
			print "Connection Refused"
		s.close()
	return
	
#main
raps = knock(host, port)
rapping(host, raps)