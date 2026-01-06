import logging
import discord
from config import load_config

settings = load_config()
intents = discord.Intents.default()
intents.message_content = True
guilds = settings.guilds
bot = discord.Bot(intents=intents)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(settings.log_format))
logger = logging.getLogger('discord')
logger.setLevel(settings.log_level)
logger.addHandler(handler)

logger = logging.getLogger('app.main')
logger.setLevel(settings.log_level)
logger.addHandler(handler)

@bot.event
async def on_ready():
    logger.info(f"Logged in as: \033[36m{bot.user.name}\033[90m#\033[37m{bot.user.discriminator}\033[0m")

# Loading the Extensions aka. cogs
registered_extensions = [ 'cogs.events',
                          'cogs.commands' ]

for extension in registered_extensions:
    if extension.startswith('!'):
        logger.info(f"Extension skipped: {extension.replace('!','')}")
    else:
        bot.load_extension(extension)
        logger.info(f"Extension loaded: {extension}")

# running the actual bot
bot.run(settings.discord_token)