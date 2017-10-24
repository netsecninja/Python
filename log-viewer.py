#!/usr/bin/env python3

# Imports
from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
import os
from ipaddress import ip_address
from operator import itemgetter

# Variables

# Class
class LogHTTPRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		date = datetime.datetime.now() # Refreshes date
		# Parse the arguments
		view = ""
		datearg = ""
		ip = ""
		argindex = self.path.find("?")
		args = self.path[argindex+1:]
		if argindex >= 0 or len(args) > 1: # If args exist
			for arg in args.split("&"):
				if "v=" in arg:
					view = arg[2:]
					if 4 <= len(view) <= 5 and (view == "stats" or view == "host" or view == "full"):
						continue
					else:
						view = "stats"
				if "d=" in arg:
					datearg = arg[2:]
					if len(datearg) == 8 and datearg.isdigit():
						date = datetime.datetime.now() # Refreshes date
						date = date.replace(month=int(datearg[0:2]),day=int(datearg[2:4]),year=int(datearg[4:]))
					else:
						date = datetime.datetime.now()
				if "i=" in arg:
					ip = arg[2:]
					if len(ip) != 0:
						try:
							ip_address(ip)
						except ValueError:
							view = "stats"
							ip = ""
		else: # Default
			date = datetime.datetime.now() # Refreshes date
			view = "stats"
			ip = ""

		# Send HTML
		self.send_response(200)
		self.send_header("Content-type","text-html")
		self.end_headers()
		html = formatOutput(date,view,ip)
		self.wfile.write(bytes(html, "utf8"))
		return

def formatOutput(date,view,ip):
	global hosts
	# Calculate dates
	minus7 = date - datetime.timedelta(days=7)
	minus1 = date - datetime.timedelta(days=1)
	plus1 = date + datetime.timedelta(days=1)
	plus7 = date + datetime.timedelta(days=7)
	
	# Format page code	
	pagecode = "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>Log Viewer</title></head><body><font size=5>"
	if view == "stats":
		pagecode += "Stats View&ensp;"
		pagecode += "<a href=?v="+view+"&d="+minus7.strftime("%m%d%Y")+"><<</a>&ensp;<a href=?v="+view+"&d="+minus1.strftime("%m%d%Y")+"><</a>&ensp;" 
		pagecode += date.strftime("%b %d %Y")		
		pagecode += "&ensp;<a href=?v="+view+"&d="+plus1.strftime("%m%d%Y")+">></a>&ensp;<a href=?v="+view+"&d="+plus7.strftime("%m%d%Y")+">>></a>&ensp;"
		pagecode += "<a href=?v="+view+"&d="+datetime.datetime.now().strftime("%m%d%Y")+">Today</a>&ensp;<a href=?v=full&d="+date.strftime("%m%d%Y")+">Full</a></font>"
		pagecode += "<hr />"
		parse(getLog(date))
		getStats()
		if len(hosts) > 0:
			for host in hosts:
				hostindex = hosts.index(host) # Find index location of host
				pagecode += "<font size=5><a href=?v=host&d="+date.strftime("%m%d%Y")+"&i=" + host + ">"+ host +"</a></font><br />"
				pagecode += formatStats(host)
		else:
			pagecode += "No logs for date"
		pagecode += "</body></html>"
	elif view == "full":
		pagecode += "Full View&ensp;"
		pagecode += "<a href=?v="+view+"&d="+minus7.strftime("%m%d%Y")+"><<</a>&ensp;<a href=?v="+view+"&d="+minus1.strftime("%m%d%Y")+"><</a>&ensp;" 
		pagecode += date.strftime("%b %d %Y")		
		pagecode += "&ensp;<a href=?v="+view+"&d="+plus1.strftime("%m%d%Y")+">></a>&ensp;<a href=?v="+view+"&d="+plus7.strftime("%m%d%Y")+">>></a>&ensp;"
		pagecode += "&ensp;<a href=?v="+view+"&d="+datetime.datetime.now().strftime("%m%d%Y")+">Today</a>&ensp;<a href=?v=stats&d="+date.strftime("%m%d%Y")+">Stats</a></font>"
		pagecode += "<hr />"
		parse(getLog(date))
		if len(hosts) > 0:
			pagecode += formatFull()
		else:
			pagecode += "No logs for date"
		pagecode += "</body></html>"
	elif view == "host":
		pagecode += "Host View&ensp;"	
		pagecode += "<a href=?v="+view+"&d="+minus7.strftime("%m%d%Y")+"&i="+ip+"><<</a>&ensp;<a href=?v="+view+"&d="+minus1.strftime("%m%d%Y")+"&i="+ip+"><</a>&ensp;" 
		pagecode += date.strftime("%b %d %Y")		
		pagecode += "&ensp;<a href=?v="+view+"&d="+plus1.strftime("%m%d%Y")+"&i="+ip+">></a>&ensp;<a href=?v="+view+"&d="+plus7.strftime("%m%d%Y")+"&i="+ip+">>></a>&ensp;"
		pagecode += "&ensp;<a href=?v="+view+"&d="+datetime.datetime.now().strftime("%m%d%Y")+"&i="+ip+">Today</a>&ensp;<a href=?v=stats&d="+date.strftime("%m%d%Y")+"&i="+ip+">Stats</a></font>"
		pagecode += "<hr />"
		parse(getLog(date))
		if len(hosts) > 0:
			pagecode += formatHost(ip)
		else:
			pagecode += "No logs for host"
		pagecode += "</body></html>"
	return pagecode

def formatStats(host):
	global hosts
	global hoststats
	stats = ""
	hostindex = hosts.index(host) # Find index location of host
	for entry in hoststats[hostindex]:				
		stats += str(entry[1]) + "&ensp;" + entry[0] + "<br />"
	stats += "<p>"
	return stats

def formatHost(host):
	global hosts
	global hostfull
	full = "<font size=5>" + host + "</font><br />"
	hostindex = hosts.index(host) # Find index location of host
	for entry in hostfull[hostindex].split("\n"):
		full += entry + "<br />"
	return full

def formatFull():
	global fulllog
	full = ""
	for entry in fulllog.split("\n"):				
		full += entry + "<br />"
	return full

def getLog(date):
	# Given date, form filename
	date = date.strftime("%Y%m%d")
	today = datetime.datetime.now().strftime("%Y%m%d") # Get today
	if date == today: # If date is today
		log = "/var/log/dns.log"
	else: # Otherwise format for the rotation log name
		log = "/var/log/dns.log-"+ date
	if os.path.isfile(log): # Check if file exists
		# Open file, read contents into variable
		f = open(log, 'r')
		raw = []
		for line in f.readlines():
			if "query[A" in line and not "127.0.0.1" in line: # Filter out only queries, and no 127.0.0.1 entries
				raw.append(line.strip())
		f.close() # Close file
		return raw
	else: # No file found
		raw = []		
		return raw

def parse(raw):
	global hosts
	global fulllog
	global hostfull
	global hoststats
	
	# Reset globals
	hosts = []
	fulllog = ""
	hostfull = []
	hoststats = []
	
	for line in raw:
		dtstamp = line[0:15] # Parse date time
		site = line[16:].split(" ")[2].split(" ")[0] # Parse query
		host = line[16:].split(" ")[4] # Parse host
		if host not in hosts: # Check against host list
			hosts.append(host) # Add to host list
			hostfull.append("") # Stage host full log
			hoststats.append("") # Stage host stats
		hostindex = hosts.index(host) # Find index location of host
		entry = dtstamp + " " + host + " " + site + "\n" # Format full log entry
		hostfull[hostindex] += entry
		fulllog += entry
	return

def getStats():
	global hosts
	global hoststats
	global hostfull
	
	for host in hosts:
		hostindex = hosts.index(host) # Find index location of host
		stats = {} # Clear temp stats dictionary
		for line in hostfull[hostindex].split("\n"):
			site = line[16:].split(" ")[-1] # Parse only the site out
			if site not in stats and site != "": # Check if already in stats dictionary
				stats[site] = hostfull[hostindex].count(site) # If not, then add it with the query count
		unsortedstats = []
		for site, count in stats.items():
			unsortedstats.append((site, count))
		hoststats[hostindex] = sorted(unsortedstats, key=itemgetter(1), reverse=True)
	return

# Main
server_address = ("",8888)
httpd = HTTPServer(server_address, LogHTTPRequestHandler)
print("HTTP server is running...")
httpd.serve_forever()


