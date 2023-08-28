import json
import discord
import datetime
from discord.commands import Option, message_command

def read_config():
    with open('config-sensitive-data.json') as f:
        return json.load(f)

intents = discord.Intents.default()
guilds = read_config()["GUILDS"]
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')


@bot.slash_command(guild_ids=guilds) 
async def zitat(ctx: discord.ApplicationContext, 
                discord_benutzer: Option(discord.Member, "Der Discord-Benutzer, der zitiert werden soll", required=True), 
                zitat: Option(str, "Der Satz, der zitiert werden soll", required=True)
                ):
    """Zitiere einen bestimmten Satz von einem Discord-Benutzer"""
    
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{zitat}`\n### {discord_benutzer.mention}\n\n_ _\n\n*Zitiert von {ctx.author.mention}*"
    )
    zitat_embed.set_thumbnail(url=discord_benutzer.avatar.url)
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{datetime.datetime.now().strftime('%H:%M | %d.%m.%Y')}")
    
    channel = bot.get_channel(read_config()["QUOTES_CHANNEL"])
    await channel.send(embed=zitat_embed)
    await ctx.respond(f'Der Benutzer {discord_benutzer.mention} wurde mit folgendem Zitat zitiert: `{zitat}` von {ctx.author.mention}!', ephemeral=True)


@bot.slash_command(guild_ids=guilds) 
async def custom_zitat(ctx: discord.ApplicationContext, 
                benutzer: Option(str, "Der Name, der zitiert werden soll", required=True),
                zitat: Option(str, "Der Satz, der zitiert werden soll", required=True)
                ):
    """Zitiere einen bestimmten Satz von einem NICHT-Discord-Benutzer"""

    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{zitat}`\n### @{benutzer.capitalize()}\n\n_ _\n\n*Zitiert von {ctx.author.mention}*"
    )
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{datetime.datetime.now().strftime('%H:%M | %d.%m.%Y')}")
    
    channel = bot.get_channel(read_config()["QUOTES_CHANNEL"])
    await channel.send(embed=zitat_embed)
    await ctx.respond(f'**@{benutzer.capitalize()}** wurde mit folgendem Zitat zitiert: `{zitat}` von {ctx.author.mention}!', ephemeral=True)

@bot.message_command(guild_ids=guilds, name="Zitieren")
async def app_zitat(ctx: discord.ApplicationContext, message):
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{message.content}`\n### {message.author.mention}\n\n_ _\n\n*Zitiert von {ctx.author.mention}*"
    )
    zitat_embed.set_thumbnail(url=message.author.avatar.url)
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{datetime.datetime.now().strftime('%H:%M | %d.%m.%Y')}")
    
    channel = bot.get_channel(read_config()["QUOTES_CHANNEL"])
    await channel.send(embed=zitat_embed)
    await ctx.respond(f'Der Benutzer {message.author.mention} wurde mit folgendem Zitat zitiert: `{message.content}` von {ctx.author.mention}!', ephemeral=True)



bot.run(read_config()["TOKEN"])