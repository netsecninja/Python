# PBDMP - Paste Bin Dump search tool
# Written by Jeremiah Bess (jeremiah.bess@gmail.com)
# Uses Python 2.7 for legacy installs
# https://psbdmp.ws/
#
# To do:
# Whitelist completed dumps
# Possible GUI?

# Imports
import urllib2 # Used in the API request
import json # Used for API return parsing

# Globals
searchURL = "https://psbdmp.ws/api/search/"
dumpURL = "https://psbdmp.ws/api/dump/get/"
searchFile = 'domainlist.txt'
searchList = []
outputFile = "results.txt"
results = ""

# Functions
def getList():
    global searchFile
    global searchList
    try:
        with open(searchFile,"r") as sf:
            for line in sf:
                if line.strip("\n") != '':
                    searchList.append(line.strip("\n"))
        sf.close()
    except:
        print "File domainlist.txt could not be found or opened. File must contain a single domain or email address per line."
        return 1

def queryAPI(query,search=False):
    try:
        if search == True:
            request = urllib2.urlopen(searchURL+query)
        else:
            request = urllib2.urlopen(dumpURL+hit["id"])
        jsonResponses = json.loads(request.read())
        if jsonResponses["error"] != 0:
            raise Exception() 
        else:
            return jsonResponses
    except:
        return 1

# Main
if getList() == 1:
    exit()
for domain in searchList:
    responses = queryAPI(domain,True)
    if responses == 1:
        print "Domain search failed for " + domain
        continue

    print "Domain: " + domain + " - " + str(responses["count"]) + " entries"
    results += "Domain: " + domain + " - " + str(responses["count"]) + " entries\r\n"

    for hit in responses["data"]:
        dump = queryAPI(hit)
        if dump == 1:
            results += "Dump search failed for " + domain + " dump " + hit + "\r\n"
            continue
        results += "===== Begin " + domain + " dump " + hit["id"] + " on " + dump["time"] + " =====\r\n"
        results += dump["data"] + "\r\n"
        results +="===== End " + domain + " dump " + hit["id"] + " on " + dump["time"] + " =====\r\n"

if results != "":
    results = results.encode("utf-8") # Required to have common encoding
    print "\r\nComplete, results are stored in results.txt."
    with open(outputFile,"w") as output:
        output.write(results)
    output.close()
else:
    print "Done. No results found."
