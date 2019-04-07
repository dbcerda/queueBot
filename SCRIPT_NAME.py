import os, discord
from discord.ext.commands import Bot

# We'll need to substitute the Prefix for an Enviroment Variable
BOT_PREFIX = os.environ['prefix']  # -Prfix is need to declare a Command in discord ex: !pizza "!" being the Prefix
TOKEN = os.environ['token']  # The token is also substituted for security reasons

client = Bot(command_prefix=BOT_PREFIX)


# this is an event which is triggered when something happens in Discord
# in this case on_ready() is called when the bot logs on
# you can checkthe Discord API Documentaion for more event Functions
# here: https://discordapp.com/developers

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name="--Insert-Game-name-here--"))


# below this line you can put custom Functions


@client.command(name="OpenQueue")
async def openQueue():
    await client.say(""+"Teste OpenQueue")

@client.command(name="closeQueue")
async def closeQueue():
    await client.say(""+"Teste CloseQueue")
	
@client.command(name="entrar")
async def entrar(message):
    await client.say(""+"teste entrar")
	
@client.command(name="sair")
async def sair(message):
    await client.say(""+"teste sair")

@client.command(name="passarVez")
async def passarVez():
    await client.say(""+"teste passarvez")
	
client.run(TOKEN)
