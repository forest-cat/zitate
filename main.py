import json
import discord
import datetime
from discord.commands import Option

def read_config():
    with open('config-sensitive-data.json') as f:
        return json.load(f)

intents = discord.Intents.default()
guilds = read_config()["GUILDS"]
bot = discord.Bot(intents=intents)



@bot.slash_command(guild_ids=guilds) 
async def zitat(ctx: discord.ApplicationContext, 
                discord_benutzer: Option(discord.Member, "Der Discord-Benutzer, der zitiert werden soll", required=True), 
                zitat: Option(str, "Der Satz, der zitiert werden soll", required=True)
                ):
    """Zitiere einen bestimmten Satz von einem Discord-Benutzer"""
    await ctx.respond(f'Der Benutzer {discord_benutzer.mention} wird jetzt mit folgendem Zitat zitiert: `{zitat}` von {ctx.author.mention}!', ephemeral=True)
    
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{zitat}`\n### {discord_benutzer.mention}\n\n_ _\n\n*Zitiert von {ctx.author.mention}*"
    )
    zitat_embed.set_thumbnail(url=discord_benutzer.avatar.url)
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{datetime.datetime.now().strftime('%H:%M | %d.%m.%Y')}")
    
    channel = bot.get_channel(read_config()["QUOTES_CHANNEL"])
    await channel.send(embed=zitat_embed)


@bot.slash_command(guild_ids=guilds) 
async def custom_zitat(ctx: discord.ApplicationContext, 
                benutzer: Option(str, "Der Name, der zitiert werden soll", required=True),
                zitat: Option(str, "Der Satz, der zitiert werden soll", required=True)
                ):
    """Zitiere einen bestimmten Satz von einem NICHT-Discord-Benutzer"""
    await ctx.respond(f'**@{benutzer.capitalize()}** wird jetzt mit folgendem Zitat zitiert: `{zitat}` von {ctx.author.mention}!', ephemeral=True)

    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{zitat}`\n### @{benutzer.capitalize()}\n\n_ _\n\n*Zitiert von {ctx.author.mention}*"
    )
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{datetime.datetime.now().strftime('%H:%M | %d.%m.%Y')}")
    
    channel = bot.get_channel(read_config()["QUOTES_CHANNEL"])
    await channel.send(embed=zitat_embed)


bot.run(read_config()["TOKEN"])