import re
import json
import pytz
import sqlite3
import discord
import datetime
from discord.commands import Option, message_command

# Todo: -Voting System (Mit Reaktionen und Usern in Datenbank JSON gelistet)
# Todo: -NUR VIELLEICHT: Role Check (Mit Erklärung/Nachricht für erstes Zitat) (Zitteraal Rolle)
# Todo: -Gruppenzitate mit mehreren Embeds (Gleiche Farbe, ohne Datenbankeintrag) !!!Voting wird hier schwierig!!!  -- mal sehen :D

def read_config():
    with open('config-sensitive-data.json') as f:
        return json.load(f)

# def analyze_sentence(input_text):
#     # Pattern to capture text between "`" characters
#     backticks_pattern = r"`(.*?)`"
    
#     # Pattern to capture text in parentheses () or asterisks *, without grouping
#     extra_info_pattern = r'\([^)]+\)|\*[^*]+\*'
    
#     # Find text between "`" characters
#     text_between_backticks = re.findall(backticks_pattern, input_text)
    
#     # Find text in parentheses () or asterisks *
#     extra_info = re.findall(extra_info_pattern, input_text)
    
#     # Extract the found text from tuples or use a default value (empty string)
#     text_between_backticks = next(iter(text_between_backticks), "")
    
#     if extra_info:
#         extra_info = ' '.join(extra_info)
#         # Remove parentheses () and asterisks * from the original text
#         cleaned_extra_info = re.sub(r'[()*]', '', extra_info)
#     else:
#         cleaned_extra_info = ""
    
#     return text_between_backticks, cleaned_extra_info

# def get_datetime(entry):
    date_time_str = entry[-1]  # Nehmen Sie das letzte Element des Eintrags (das Datum und die Uhrzeit)
    return datetime.datetime.strptime(date_time_str, '%d.%m.%Y | %H:%M')


intents = discord.Intents.default()
intents.message_content = True
guilds = read_config()["GUILDS"]
bot = discord.Bot(intents=intents)
database = read_config()["DATABASE"]


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Zitate (
                    ID INTEGER PRIMARY KEY,
                    Zitat_User_Name TEXT,
                    Writer_User_Name TEXT,
                    Zitat_User_ID INTEGER, 
                    Writer_User_ID INTEGER, 
                    Zitat TEXT,
                    Context TEXT,
                    Date TEXT,
                    Message_ID INTEGER,
                    Rating INTEGER,
                    Rating_User_IDs TEXT
                )''')
    # Änderungen speichern
    conn.commit()
    # Verbindung schließen
    conn.close()


@bot.slash_command(guild_ids=guilds)
async def zitat(ctx: discord.ApplicationContext,
                discord_benutzer: Option(discord.Member, "Der Discord-Benutzer, der zitiert werden soll", required=True), 
                zitat: Option(str, "Der Satz, der zitiert werden soll", required=True),
                kontext: Option(str, "Möglicher Kontext um das Zitat zu verstehen", required=False)=""):
    """Zitiere einen bestimmten Satz von einem Discord-Benutzer"""
    
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{zitat}`\n{kontext if kontext == '' else f'({kontext})'}\n### {discord_benutzer.mention}\n\n\n# 0\n*Zitiert von {ctx.author.mention}*")
    zitat_embed.set_thumbnail(url=discord_benutzer.avatar.url)
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{datetime.datetime.now().strftime('%d.%m.%Y | %H:%M')}")
    
    channel = bot.get_channel(read_config()["QUOTES_CHANNEL"])
    message = await channel.send(embed=zitat_embed)
    await ctx.respond(f'Der Benutzer {discord_benutzer.mention} wurde mit folgendem Zitat zitiert: `{zitat}` von {ctx.author.mention}!', ephemeral=True)
    
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO Zitate (
                           Zitat_User_Name, 
                           Writer_User_Name, 
                           Zitat_User_ID, 
                           Writer_User_ID, 
                           Zitat, 
                           Context, 
                           Date,
                           Message_ID,
                           Rating,
                           Rating_User_IDs
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                           (discord_benutzer.display_name, 
                            ctx.author.display_name, 
                            discord_benutzer.id, 
                            ctx.author.id, 
                            zitat, 
                            kontext, 
                            datetime.datetime.now().astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M"),
                            message.id,
                            0,
                            json.dumps([])
                            ))
    # Änderungen speichern
    conn.commit()
    # Verbindung schließen
    conn.close()
    

@bot.slash_command(guild_ids=guilds) 
async def custom_zitat(ctx: discord.ApplicationContext, 
                benutzer: Option(str, "Der Name, der zitiert werden soll", required=True),
                zitat: Option(str, "Der Satz, der zitiert werden soll", required=True),
                kontext: Option(str, "Möglicher Kontext um das Zitat zu verstehen", required=False)=""):
    """Zitiere einen bestimmten Satz von einem NICHT-Discord-Benutzer"""
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{zitat}`\n{kontext if kontext == '' else f'({kontext})'}\n### @{benutzer.capitalize()}\n\n\n# 0\n*Zitiert von {ctx.author.mention}*")
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{datetime.datetime.now().strftime('%d.%m.%Y | %H:%M')}")
    
    channel = bot.get_channel(read_config()["QUOTES_CHANNEL"])
    message = await channel.send(embed=zitat_embed)
    await ctx.respond(f'**@{benutzer.capitalize()}** wurde mit folgendem Zitat zitiert: `{zitat}` von {ctx.author.mention}!', ephemeral=True)
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO Zitate (
                           Zitat_User_Name, 
                           Writer_User_Name, 
                           Zitat_User_ID, 
                           Writer_User_ID, 
                           Zitat, 
                           Context, 
                           Date,
                           Message_ID,
                           Rating,
                           Rating_User_IDs
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                           (benutzer.capitalize(), 
                            ctx.author.display_name, 
                            0, 
                            ctx.author.id, 
                            zitat,
                            kontext, 
                            datetime.datetime.now().astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M"),
                            message.id,
                            0,
                            json.dumps([])
                            ))
    # Änderungen speichern
    conn.commit()
    # Verbindung schließen
    conn.close()


@bot.message_command(guild_ids=guilds, name="Zitieren")
async def app_zitat(ctx: discord.ApplicationContext, message):
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{message.content}`\n### {message.author.mention}\n\n({message.jump_url})\n# 0\n*Zitiert von {ctx.author.mention}*"
    )
    zitat_embed.set_thumbnail(url=message.author.avatar.url)
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{datetime.datetime.now().strftime('%d.%m.%Y | %H:%M')}")
    
    channel = bot.get_channel(read_config()["QUOTES_CHANNEL"])
    new_message = await channel.send(embed=zitat_embed)
    await ctx.respond(f'Der Benutzer {message.author.mention} wurde mit folgendem Zitat zitiert: `{message.content}` von {ctx.author.mention}!', ephemeral=True)

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO Zitate (
                           Zitat_User_Name, 
                           Writer_User_Name, 
                           Zitat_User_ID, 
                           Writer_User_ID, 
                           Zitat, 
                           Context, 
                           Date,
                           Message_ID,
                           Rating,
                           Rating_User_IDs
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                           (message.author.display_name, 
                            ctx.author.display_name, 
                            message.author.id, 
                            ctx.author.id, 
                            message.content,
                            '', 
                            datetime.datetime.now().astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M"),
                            new_message.id,
                            0,
                            json.dumps([])
                            ))
    # Änderungen speichern
    conn.commit()
    # Verbindung schließen
    conn.close()


# @bot.slash_command(guild_ids=guilds)
# @discord.default_permissions(administrator=True)
# async def dump_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
#     """Dumpt alle Zitat-Nachrichten eines Channels (Im richtigen Format) in die Datenbank"""
#     print(f"Dumping channel {channel.name}...")
#     await ctx.respond(f"Dumping channel {channel.mention}...", ephemeral=True)
#     conn = sqlite3.connect(database)
#     cursor = conn.cursor()
#     for message in await channel.history(limit=None).flatten():
#         if len(message.mentions) == 1:
#             zitat, context = analyze_sentence(message.content)
#             print(zitat, context)
#             cursor.execute("""INSERT INTO Zitate (
#                            Zitat_User_Name, 
#                            Writer_User_Name, 
#                            Zitat_User_ID, 
#                            Writer_User_ID, 
#                            Zitat, 
#                            Context, 
#                            Date
#                            ) VALUES (?, ?, ?, ?, ?, ?, ?)""", 
#                            (message.mentions[0].display_name, 
#                             message.author.display_name, 
#                             message.mentions[0].id, 
#                             message.author.id, 
#                             zitat, 
#                             context, 
#                             message.created_at.astimezone(
#                                 pytz.timezone("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M")))
#         else:
#             print(f"Message was not right formatted: '{message.content}'")
#     # Änderungen speichern
#     conn.commit()
#     # Verbindung schließen
#     conn.close()
#     print("Done!")

# @bot.slash_command(guild_ids=guilds)
# @discord.default_permissions(administrator=True)
# async def send_zitate(ctx: discord.ApplicationContext, channel: discord.TextChannel):
#     """Sendet alle Zitate aus der Datenbank in einen Channel"""
#     print(f"Sending zitate to channel {channel.name}...")
#     await ctx.respond(f"Sending zitate to channel {channel.mention}...", ephemeral=True)
#     # Verbindung zur Datenbank herstellen
#     conn = sqlite3.connect('meine_datenbank.db')
#     cursor = conn.cursor()

#     # Daten abfragen
#     cursor.execute("SELECT * FROM Zitate")
#     rows = cursor.fetchall()

#     # Verbindung schließen
#     conn.close()

#     sorted_entries = sorted(rows, key=get_datetime)

#     print("Sorted:")
#     for row in sorted_entries[::-1]:
#         print(row)

        
#         zitat_embed = discord.Embed(
#             color=discord.Color.random(),
#             description=f"## `{row[5]}`\n{'' if row[6] == '' else f'({row[6]})'}### {f'@{row[1]}' if row[3] == 0 else f'<@{row[3]}>'}\n\n_ _\n\n*Zitiert von <@{row[4]}>*"
#         )

#         zitat_embed.set_thumbnail(url=discord.Embed.Empty.url if row[3] == 0 else (await bot.fetch_user(row[3])).avatar.url)
#         zitat_embed.set_footer(icon_url=(await bot.fetch_user(row[4])).avatar.url, text=f"{row[7]}")
        
#         await channel.send(embed=zitat_embed)
    
#     print("Done!")

bot.run(read_config()["TOKEN"])