from datetime import datetime
from pathlib import Path
import logging
import discord
import json
import os



# Header Variables
header_filename = ""
header = {}

# Constants
token = ""
guild_id = ""
uwu_channel_id = ""
main_channel_id = ""
whitelist = {} # bot, me
last_message = ""

# Discord Client Object
client = discord.Client()



# Initialize the Logger
def init_logger(log_level="INFO"):

	# Add Log File to Log Folder
	logs_path = os.path.join(Path().absolute(), "logs")
	Path(logs_path).mkdir(parents=True, exist_ok=True)
	logs_file = os.path.join(logs_path, f"uwu_bot.log", )

	handler = logging.FileHandler(logs_file, 'a', 'utf-8')
	handler.setFormatter(logging.Formatter('%(asctime)s (%(levelname)s) --> %(message)s', datefmt='%m-%d-%y %H:%M:%S'))

	logger = logging.getLogger("Log")
	logger.addHandler(handler)

	temp_file = open(logs_file, 'a')
	temp_file.write("\n" + '-'*64 + "\n\n")
	temp_file.close()
	
	# Set Log Level
	log_level = str(log_level).upper()
	if log_level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
		logger.setLevel(eval("logging." + log_level))
	else:
		raise Exception

	return logger



# Load the Header and Pull Constants
def load_header():
	global header_filename
	global header

	global token
	global guild_id
	global uwu_channel_id
	global main_channel_id
	global whitelist
	global last_message

	# Generate filepath
	dirname = os.path.dirname(__file__)
	header_filename = os.path.join(dirname, 'header.json')

	# Open the file and save it
	file = open(header_filename, 'r')
	header = json.load(file)
	file.close()

	# Load variables
	token = header['TOKEN']
	guild_id = header['GUILD ID']
	uwu_channel_id = header['UWU CHANNEL ID']
	main_channel_id = header['MAIN CHANNEL ID']
	whitelist = header['WHITELIST']
	last_message = datetime.utcfromtimestamp(header['last_update'])
	


# Get the Current UNIX Timestamp and Update the Header File
def save_header():
	global header

	# Update dict.
	header["last_update"] = datetime.now().timestamp()

	# Dump JSON into File
	file = open(header_filename, "w")
	json.dump(header, file, indent='\t', separators=(',',' : '))
	file.close()



# Checks if the Specified Text is a Valid 'UwU'
def is_uwu(text):
	text = str(text).lower()
	text_arr = text.split(" ")
	
	# Split the message into words
	for word in text_arr:

		# Make sure each word contains 'uwu'
		if 'uwu' in word:

			# Make sure there are no other alphanumeric characters in the word
			word = word.replace("uwu", "")
			for char in word:
				if char.isalnum():
					break
		else:
			break
	else:
		return True
	return False



# Punishes a Non-UwU Message
async def punish(message):
	logger.info("Shaming " + str(message.author.name))

	"""
	if str(message.author.id) not in whitelist:
		# Remove the User From the Channel
		await message.channel.set_permissions(message.author, read_messages=False)
	else:
		logger.info("User is Whitlisted")
	"""

	# Shame the User in Some Other Channel
	c = await client.fetch_channel(main_channel_id)
	await c.send(content=f'<@{message.author.id}> Was Removed From The UwU Channel For Sending A Non-UwU Message! :oncoming_police_car: :rotating_light:')



# Runs Once the Bot Has Connected to the Guild
@client.event
async def on_ready():
	logger.info("Checking Previous Messages...")

	c = await client.fetch_channel(uwu_channel_id)
	async for msg in c.history(after=last_message):

		if not is_uwu(msg.content):
			logger.info(f'Deleting message from {msg.author.name}')

			# Remove the User from the Channel if Possible
			await punish(msg)

			# Delete the Message
			await msg.delete()
	
	logger.info("Initialized Successfully")


	
# Runs when a message is sent in the guild
@client.event
async def on_message(message):

	# Only Check the Channel of Interest
	if str(message.author.guild.id) != guild_id or str(message.channel.id) != uwu_channel_id:
		return

	logger.info(f'{message.author.name} said "{message.content}": ' + ("Valid UwU" if is_uwu(message.content) else "Not UwU"))
	
	# Handle Non-UwU Messages
	if not is_uwu(message.content):

		# Remove the User from the Channel if Possible
		await punish(message)

		# Delete the Message
		await message.delete()
		logger.info("Message Deleted")



# Get Logger Object
logger = init_logger()
logger.info("New Session Started")


# Main Program
try:
	# Load the Header File
	load_header()

	# Run the App
	client.run(token)

# Handle Exceptions
except KeyboardInterrupt:
	pass
except BaseException as err:
	logger.error(err)

# Save the Timestamp When we Finished
finally:
	save_header()
	logger.info("Session Ended. Goodbye...")
