from fuzzywuzzy import process
import discord
import json
import os


# Discord Client Object
client = discord.Client()



# Lists all commands and emotes
async def list_all(channel):

	# List Emotes
	desc = ", ".join(["Worry" + str(asset) for asset in asset_names ])

	# Send Message
	await channel.send(embed=discord.Embed(title="__Emotes:__",description=desc, color=3190807))



# Runs when a message is sent in the guild
@client.event
async def on_message(message: discord.Message):

	# Check for keyword
	msg = str(message.content)
	if (message.author.id == client.user.id) or ("Worry" not in msg):
		return

	# Parse Command
	start = msg.find("Worry") + 5
	next_space = msg.find(' ', start)
	if next_space < 0: next_space = len(msg)
	substr = msg[ start : next_space ]

	channel = client.get_channel(message.channel.id)

	# List Command
	if substr == "List":
		await list_all(channel)

	# Emote
	else:
		# Perfect Match
		if substr in asset_names:
			filename = asset_paths[asset_names.index(substr)]
			filepath = os.path.join(dirname, "assets/" + filename)
			await channel.send(file=discord.File(filepath, filename=filename))

		# Fuzzy Match
		else:
			best_match = process.extract(substr, asset_names)[0]
			if best_match[1] > 50:
				await channel.send(content="'Worry" + substr + "' not recognized. Did you mean 'Worry" + best_match[0] + "'?")
			else:
				await channel.send(content="Command Not Recognized. Use 'WorryList' to list all commands/emotes")



# Generate filepath
dirname = os.path.dirname(__file__)
header_filename = os.path.join(dirname, 'secrets.json')

# Open the file and save it
with open(header_filename, 'r') as file:
	header = json.load(file)
	file.close()

# Load Settings
asset_paths = []
assets_path = os.path.join(dirname, "assets/")
for f in os.listdir(assets_path):
	if os.path.isfile( os.path.join(assets_path, f) ):
		asset_paths.append(f)

asset_names = [os.path.splitext(f)[0] for f in asset_paths]
token  = header["token"]


# Start Bot
try:
	print("Running...")
	client.run(token)
except BaseException as err:
	pass
finally:
	print("Goodbye")