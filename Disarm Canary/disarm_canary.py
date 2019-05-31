#!/usr/bin/python3
'''
Title: Canary token disarming script
Version: 1.0
Created by: Jeremiah Bess - jeremiah.bess@gmail.com
Description: Script will remove canary tokens found in Microsoft Word documents
Example: http://canarytokens.com URL found in word/footer1.xml and word/_rels/footer1.xml.rels
Resources:
* https://towardsdatascience.com/how-to-extract-data-from-ms-word-documents-using-python-ed3fbb48c122
To do:
[] Look for other canary token methods with Office docs
[] Consider other file types for script to work with
'''

# Imports
import zipfile # Manipulate zip files (Office docs)
import re # Search for URLs
import argparse # Parse command arguments

# Global variables
ignores = ['schemas','purl.org','w3.org']  # Whitelisted strings in URLs
linklist = []

# Functions
def getZip():  # Argument parser
    global zipped
    global filename
    parser = argparse.ArgumentParser(description='Canary token disarming script')
    parser.add_argument('filename', nargs=1, help='Provide a filename to search for canary tokens')
    args = parser.parse_args()
    filename = args.filename[0]
    try:
        zipped = zipfile.ZipFile(filename)
        return zipped
    except:
        print('Unable to open document:', args.filename[0])
        exit()

def getLinks():  # Collect all http/s URLs
    global zipped
    global linklist
    for file in zipped.namelist():
        content = str(zipped.read(file))
        links = re.findall('http.*?[^"]+',content)
        for link in links:
            if not checkIgnores(link):  # Omit URLs with whitelisted strings
                if link not in linklist:  # Verify link does not already exist
                    linklist.append(link)
    return

def checkIgnores(link):  # Omit URLs with whitelisted strings
    for ignore in ignores:
        if ignore in link:
            return True
    return False

def getActions():
    global linklist
    # Print list
    for index, link in enumerate(linklist):
        print(str('[' + str(index+1) + '] ' + link))  # Set index referenced to 1
    # Determine actions
    action = input(
        '\nEnter which URLs numbers to disarm separated by commas, [A] for all, or hit [Enter] to do nothing: ')
    action.replace(' ', '')  # Remove whitespace
    # Validate input
    if re.search('^(\d+,*)+$', action):  # Remove list of links
        newlinklist = []
        for num in action.split(','):
            index = int(num)-1  # Reset index referenced to 0
            newlinklist.append(linklist[index])
        linklist = newlinklist  # Rebuild list with choices
        return
    elif re.search('^[aA]{1}$', action):  # Remove all links)
        return
    else:
        print('Exiting')
        exit()

def removeLinks():
    print('Removing links...', end='')
    global zipped
    name, _, ext = filename.rpartition('.')  # Get old zip filename and extension
    newfilename = name + '-nocanary.' + ext  # Set new zip filename
    newzipped = zipfile.ZipFile(newfilename,'w')  # Create new zip file
    for file in zipped.filelist:
        content = str(zipped.read(file))  # Read content
        for url in linklist:
            content = content.replace(url,'')  # Remove URL
        newzipped.writestr(file, content)  # Write modified file into new zip
    print('done!\nDisarmed file named ' + newfilename + ' has been created.')
    return

# Main
if __name__ == '__main__':
    getZip()
    getLinks()
    getActions()
    removeLinks()
