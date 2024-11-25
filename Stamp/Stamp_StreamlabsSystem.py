import clr
import sys
import json
import os
import ctypes
import codecs

ScriptName = "Stamp Sign-in"
Website = "https://www.github.com/"
Description = "Card Stamping for Streamlabs Bot"
Creator = "Anon"
Version = "0.1.0"

configFile = "config.json"
settings = {}

# My goal was to unify the different !stamp commands into a single command.

# Users can use either !stamp by itself, 
# or can use !stamp <stamp_number> <card>
# e.g.
# !stamp, !stamp 1, and !stamp 1 d are all valid usage.
# "g" signifies the gold card, while "d" signifies the diamond card.


# Near as I can tell, up-to-date membership tier information can only be retrieved from Youtube's 
# members API endpoint.  Accessing the API requires jumping through a considerable number 
# of hoops involving OAuth, so you might be better off treating cards like stamps that users can 
# earn by being members, and just keep track of that information locally yourself.  Especially 
# because accessing the API requires you to handle secrets associated with your Youtube channel, 
# which may not be attractive from a security standpoint.


# Anyway, user stamp information would be retrieved 
# from a local JSON that you manually update.
userStampInfo = "user_stamps.json"
# For example:
exampleStampJson =  {
        
        "1": ["User1", "User2", "User3"],

        "2": ["User1", "User2", "User3"]

    }


# Same with card info.
userCardInfo = "user_cards.json"


def ScriptToggled(state):
	return


def Init():
	global settings

	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
	except:

		# DEBUG
		# NOTE
		# Configured for testing purposes, you can change the permission,
		# userCooldown, and response as needed before reimporting the script.
		# Make sure to change the values in UI_Config.json as well.
		settings = {
			"liveOnly": True,
			"command": "!stamp",
			"permission": "Everyone",
			#"permission": "Sponsor",
			"useCooldown": True,
			"useCooldownMessages": True,
			"userCooldown": 1,
			#"userCooldown": 43200,
			"allowStamps": True,
			"allowCards": True,
			"onUserCooldown": "$user, you've already signed in!",
			"response": "Welcome, $user! you signed in with stamp $stamp on card $card!  you've signed in $points times!",
			#"response": "Welcome, $user! you've signed in $points times!",
		}




def Execute(data):
	
	# Filter messages for !stamp commands
	if data.IsChatMessage() and data.GetParam(0).lower() == settings["command"]:

		# User must meet permission level
		if not Parent.HasPermission(data.User, settings["permission"], ""):
			return
			
		# Stream must be live to !stamp
		if settings["liveOnly"]:
			if not Parent.IsLive():
				return

		outputMessage = ""
		userId = data.User			
		userName = data.UserName
		

		# Check whether the command is on cooldown
		if settings["useCooldown"] and Parent.IsOnUserCooldown(ScriptName, settings["command"], userId):
			if settings["useCooldownMessages"]:
				outputMessage = settings["onUserCooldown"]
				outputMessage = outputMessage.replace("$user", userName)
			else:
				outputMessage = ""
		
		
		# Check the command for parameters, and the user's eligibility 
		# for the provided stamp number and card type.
		else:
			
			# "0" is the default sign-in stamp, and
			# will be used if no optional parameter
			# is provided, or if the parameter is invalid.
			stampNumber = "0"

			# "n" is the default card type, and ditto.
			cardType = "n"

			if data.GetParamCount() > 1 and settings["allowStamps"]:
				stampNumber = CheckStampValidity(data.GetParam(1), userName)
			if data.GetParamCount() > 2 and settings["allowCards"]:
				cardType = CheckCardValidity(data.GetParam(2), userName)

			
			# Send the values to OBS or whatever you use to
			# display the card scene.  I don't know enough
			# about streaming software to know how you're
			# actually doing this, so implementing this one is up to you.
			SendToOBS(userName, stampNumber, cardType)


			# Give the user a point, and apply the cooldown.
			Parent.AddPoints(userId, userName, 1)

			if settings["useCooldown"]:
				Parent.AddUserCooldown(ScriptName, settings["command"], userId, settings["userCooldown"])

			# Set the output message.
			points = Parent.GetPoints(userId)
			outputMessage = settings["response"]

			outputMessage = outputMessage.replace("$user", userName)
			outputMessage = outputMessage.replace("$points", str(points))

			# DEBUG
			# NOTE
			# These are here for the test response message, and can be deleted
			# when you revert to the original response message.
			outputMessage = outputMessage.replace("$stamp", stampNumber)
			outputMessage = outputMessage.replace("$card", cardType)

		
		# Post the result into the chat.
		Parent.SendStreamMessage(outputMessage)
	

	return




def ReloadSettings(jsonData):
	Init()
	return


def Tick():
	return



def LoadUserInfo(infoType):
	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, infoType), encoding='utf-8-sig', mode='r') as file:
			info = json.load(file, encoding='utf-8-sig')
	except:
		info = {}
	
	return info


def CheckStampValidity(stampNumber, userName):
	stampInfo = LoadUserInfo(userStampInfo)

	# The stamp number must be present in the stamp info JSON.
	if stampNumber not in stampInfo:
		return "0"
	
	# The user must possess the stamp.
	if userName not in stampInfo[stampNumber]:
		return "0"

	return stampNumber


def CheckCardValidity(cardType, userName):
	cardInfo = LoadUserInfo(userCardInfo)

	# The card type must be present in the card info JSON.
	if cardType not in cardInfo:
		return "n"
	
	# The user must possess the card.
	if userName not in cardInfo[cardType]:
		return "n"

	return cardType



# to do
def SendToOBS(userName, stampNumber, cardType):
	return
