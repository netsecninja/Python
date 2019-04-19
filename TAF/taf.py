#!/usr/bin/python3
# Text Adventure Framework
# Version 1.0
# Created by Jeremiah Bess
# To do:
# Check if results count is equal or less than actions count
# Add health points, conditions, inventories.
# Ask for name to use in adventure
# Option to save location in adventure

# Create an adventure.cfg file in the same directory. File set up as follows:
# [Example] # Unique name of situation. Use "Start" for first situation
# Desc = Description of this situation # Free text description to display to player
# Actions = Act1,Act2 # Comma-separated list of actions to choose from. Player will choose a number that represents each. Leave this blank for no actions available, but include a single result below.
# Results = Res1,Res2 # Comma-separated list of next situation name to load that corresponds to the order of Actions above. List only one if the same result applies to all actions.

# Imports
import configparser
import os

# Global variables
story = configparser.ConfigParser()
situation = "Start" # Default starting port
adventure = "adventure.cfg" # Default adventure file

# Functions
def checkConfig():
	global situation
	if not story.has_section(situation): # Verify the situation exists in the adventure file
		print("The adventure does not have a situation for " + situation)
		exit()
	elif not story.has_option(situation,"Description") or not story.has_option(situation,"Actions") or not story.has_option(situation,"Results"): # Verify all the parts are there
		print("This situation is not completely filled out")
		exit()
	else:
		return # All is good
		
def runStory():
	global situation
	print(story.get(situation,"Description")) # Print the situation description
	count = 1 # Set the option count as 1 to start
	actions = story.get(situation,"Actions").split(",") # Collect all the actions
	if len(actions) > 1: # Check if there is more than 0 actions (split list will call no actions as 1, not 0)
		print() # Formatting line
		for action in actions:
			print(str(count) + ") " + action) # print a number and the action
			count += 1 # Increment the action count
		print("0) Quit") # Add a way to quit
	results = story.get(situation,"Results").split(",") # Collect all the results
	if len(results) > 1: # Check if there are 0 results
		while True: # Loop until we get a good answer
			result = str(input("What would you like to do? ")) # Get the user input
			if not result.isdigit(): # Verify it's a number
				print("Invalid choice")
			elif int(result) > len(results) or int(result) < 0: # Verify it's not more than the results listed or a negative number
				print("Invalid choice")
			elif int(result) == 0: # If it's 0, quit
				print("Goodbye!")
				exit()
			else:
				break
		situation = results[int(result)-1] # Change the situation to the choice made
	else:
		situation = story.get(situation,"Results") # Change the situation to the only choice
	print("===")

# Main
if os.path.isfile(adventure): # Verify the adventure file exists
	story.read(adventure) # Read the contents of the adventure file
	if os.name == "posix":
		os.system("clear") # Clear the screen on Linux
	else:
		os.system("cls") # Clear the screen on Windows
	while True: # Loop the adventure
		checkConfig() # Check all the parts are there
		runStory() # Run the adventure situation
else: # Error message if file does not exist
	print("The " + adventure + " file is missing from this directory")
	exit()	
	


