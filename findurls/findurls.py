#!/usr/bin/python3
'''
Title: Find URLs
Version: 1.1
Created by: Jeremiah Bess - jeremiah.bess@gmail.com
Description: Script find and output all URLs in office documents
Resources:
* https://towardsdatascience.com/how-to-extract-data-from-ms-word-documents-using-python-ed3fbb48c122
Revisions:
1.0 - 23 Aug 2019 - Initial release
1.1 - 26 Aug 2019 - Improved regex match syntax, added query for file://, and changed to case insensitive regex

To do:
- Set so any links in *_rels display the associated XML element to show technique used
'''

# Imports
import zipfile # Manipulate zip files (Office docs)
import re # Search for URLs
import argparse # Parse command arguments

# Global variables
ignores = ['schemas','purl.org','w3.org']  # Whitelisted strings in URLs

# Functions
def getZip():  # Argument parser
    global zipped
    parser = argparse.ArgumentParser(description='Find URLs script')
    parser.add_argument('filename', nargs=1, help='Provide a filename to search for URLs')
    args = parser.parse_args()
    filename = args.filename[0]
    try:
        zipped = zipfile.ZipFile(filename)
        return zipped
    except:
        print('Unable to open document:', args.filename[0])
        exit()

def getLinks():  # Collect all URLs
    global zipped
    linklist = []
    for file in zipped.namelist():
        content = str(zipped.read(file))
        links = re.findall('(?:https?|file):\/\/[^\"&]*',content,flags=re.IGNORECASE)
        for link in links:
            if not checkIgnores(link):  # Omit URLs with whitelisted strings
                if link not in linklist:  # Verify link does not already exist
                    linklist.append(link)
                    print(link)
    return

def checkIgnores(link):  # Omit URLs with whitelisted strings
    for ignore in ignores:
        if ignore in link:
            return True
    return False

# Main
if __name__ == '__main__':
    getZip()
    getLinks()

