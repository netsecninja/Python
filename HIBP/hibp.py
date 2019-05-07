#!/usr/bin/python3
'''
Title: Have I Been Pwned API script
Version: 0.1
Created by: Jeremiah Bess - jeremiah.bess@gmail.com
Description: Script query HIBP API for a list of email addresses, and output breaches found
'''

# Imports
try:
    import requests
except ModuleNotFoundError:
    print('Requests module not found. Use "pip install requests" to install.')
    exit()
from time import sleep

# Global variables
apiurl = 'https://haveibeenpwned.com/api/v2/breachedaccount/'
header = {'User-Agent': 'HIBP Python'}
emailfile = 'emaillist.txt'
outputfile = 'breaches.txt'
emaillist = []
results = {}

# Functions
def getemails():
    global emaillist
    try:
        with open(emailfile, 'r') as f:
            for line in f.readlines():
                emaillist.append(line.strip())
    except:
        print('Missing file. Please create', emailfile, 'with one email per line')

def callapi():
    global results
    for email in emaillist:
        request = requests.get(apiurl+email, headers=header)
        if request.ok:
            json_response = request.json()
            for entry in json_response:
                site = entry['Title']
                if email not in results.keys():
                    results[email] = [site]
                elif site not in results[email]:
                    results[email].append(site)
        else:
            results[email] = []
        sleep(1.5)

def saveoutput():
    with open(outputfile, 'w') as f:
        for email in results.keys():
            sites = ''
            for site in results[email]:
                sites += site + ','
            sites = sites.strip(',')
            output = '"' + email + '","' + sites + '"'
            print(output)
            f.write(output + '\r\n')

# Main
getemails()
callapi()
saveoutput()
