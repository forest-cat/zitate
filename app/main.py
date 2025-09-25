
import json
import logging

import pytz
import sqlite3
import discord
import datetime
from discord.ext import commands
from discord.commands import Option, message_command

from config import load_config

settings = load_config()
intents = discord.Intents.default()
intents.message_content = True
guilds = settings.guilds
bot = discord.Bot(intents=intents)
database = settings.db_filename

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(settings.log_format))
logger = logging.getLogger('discord')
logger.setLevel(settings.log_level)
logger.addHandler(handler)

@bot.event
async def on_ready(): # Creating the database if it doesn't exist
    logger.info(f'Logged in as {bot.user}!')
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
                    Rating_User_IDs TEXT,
                    Zitat_Type INTEGER
                )''')
    conn.commit()
    conn.close()

@bot.event
async def on_raw_reaction_add(reaction): # Handling the Rating System over the Reactions
    if reaction.member == bot.user:
        return
    if reaction.emoji.id not in [settings.upvote_emoji_id, settings.downvote_emoji_id]:
        return
    
    # Searching if the message is in the database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Zitate WHERE Message_ID = ?", (reaction.message_id,))
    rows = cursor.fetchall()
    if len(rows) < 1:
        return
    row = rows[0]

    channel = bot.get_channel(settings.quotes_channel)
    message = await channel.fetch_message(reaction.message_id)
    embed = message.embeds[0]
    await message.remove_reaction(reaction.emoji, reaction.member)
    
    if reaction.emoji.id == settings.upvote_emoji_id: # Handling if the user upvotes a quote
        json_obj = json.loads(row[10])
        rating = int(row[9]) + 1
        if reaction.member.id not in json.loads(row[10]):
            json_obj.append(reaction.member.id)
            cursor.execute("UPDATE Zitate SET Rating = ?, Rating_User_IDs = ? WHERE Message_ID = ?", (rating, json.dumps(json_obj), reaction.message_id))
            conn.commit()
            embed.fields[0].value = str(rating)
            await message.edit(embed=embed)
        else:
            await reaction.member.send(f"Du hast bereits für dieses Zitat (https://discord.com/channels/{reaction.guild_id}/{reaction.channel_id}/{reaction.message_id}) gevotet!")
        if rating >= 10: # Pinning the quote if the rating is 5 or higher
            await message.pin()
    elif reaction.emoji.id == settings.downvote_emoji_id: # Handling if the user downvotes a quote
        json_obj = json.loads(row[10])
        rating = int(row[9]) - 1
        if reaction.member.id not in json.loads(row[10]):
            json_obj.append(reaction.member.id)
            cursor.execute("UPDATE Zitate SET Rating = ?, Rating_User_IDs = ? WHERE Message_ID = ?", (rating, json.dumps(json_obj), reaction.message_id))
            conn.commit()
            embed.fields[0].value = str(rating)
            await message.edit(embed=embed)
        else:
            await reaction.member.send(f"Du hast bereits für dieses Zitat (https://discord.com/channels/{reaction.guild_id}/{reaction.channel_id}/{reaction.message_id}) gevotet!")
        if rating <= -3: # Deleting the quote if the rating is -3 or lower
            await message.delete()
            cursor.execute("DELETE FROM Zitate WHERE Message_ID = ?", (reaction.message_id,))
            conn.commit()

@bot.event
async def on_application_command_error(ctx, error): # Catching specific errors from the slash commands
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.respond(f"Bitte warte noch `{round(error.retry_after, 1)} Sekunden` und probiere es dann erneut", ephemeral=True)
    elif isinstance(error, commands.errors.MissingRole):
        await ctx.respond(f"Dir fehlt dazu leider die <@&{settings.quote_permission_role}> Rolle", ephemeral=True)
    else:
        raise error

@bot.slash_command(guild_ids=guilds) # The normal /zitat command
@commands.cooldown(1, settings.quote_cooldown, commands.BucketType.user)
@commands.has_role(settings.quote_permission_role)
async def zitat(ctx: discord.ApplicationContext,
                discord_benutzer: Option(discord.Member, "Der Discord-Benutzer, der zitiert werden soll", required=True),
                zitat: Option(str, "Der Satz, der zitiert werden soll", required=True),
                kontext: Option(str, "Möglicher Kontext um das Zitat zu verstehen", required=False)=""):
    """Zitiere einen bestimmten Satz von einem Discord-Benutzer"""
    # Preventing problems with the length of the zitat and kontext because discords max embed description length is 4096
    if len(zitat) > 1500:
        await ctx.respond("Leider ist das Zitat zu lang (maximal `1500` Zeichen), bitte kürze es ein wenig", ephemeral=True)
        return
    if len(kontext) > 400:
        await ctx.respond("Leider ist der Kontext zu lang (maximal `400` Zeichen), bitte kürze ihn ein wenig", ephemeral=True)
        return
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{zitat}`\n{kontext if kontext == '' else f'({kontext})'}\n## {discord_benutzer.mention}")
    zitat_embed.set_thumbnail(url=discord_benutzer.avatar.url if discord_benutzer.avatar else discord_benutzer.default_avatar.url)
    zitat_embed.add_field(name="Rating", value="0", inline=False)
    zitat_embed.add_field(name="Zitiert von", value=f"{ctx.author.mention}", inline=False)
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url, text=f"{datetime.datetime.now().strftime('%d.%m.%Y | %H:%M')}")
    
    channel = bot.get_channel(settings.quotes_channel)
    message = await channel.send(embed=zitat_embed)
    await ctx.respond(f'Der Benutzer {discord_benutzer.mention} wurde mit folgendem Zitat zitiert: `{zitat}` von {ctx.author.mention}!', ephemeral=True)
    await message.add_reaction(f"<:{settings.upvote_emoji_name}:{settings.upvote_emoji_id}>")
    await message.add_reaction(f"<:{settings.downvote_emoji_name}:{settings.downvote_emoji_id}>")
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    # Inserting the quote into the database
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
                           Rating_User_IDs,
                           Zitat_Type
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                           (discord_benutzer.display_name, 
                            ctx.author.display_name, 
                            discord_benutzer.id, 
                            ctx.author.id, 
                            zitat, 
                            kontext, 
                            datetime.datetime.now().astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M"),
                            message.id,
                            0,
                            json.dumps([]),
                            0
                            ))
    conn.commit()
    conn.close()
    

@bot.slash_command(guild_ids=guilds) # The /custom_zitat command
@commands.cooldown(1, settings.quote_cooldown, commands.BucketType.user)
@commands.has_role(settings.quote_permission_role)
async def custom_zitat(ctx: discord.ApplicationContext, 
                benutzer: Option(str, "Der Name, der zitiert werden soll", required=True),
                zitat: Option(str, "Der Satz, der zitiert werden soll", required=True),
                kontext: Option(str, "Möglicher Kontext um das Zitat zu verstehen", required=False)=""):
    """Zitiere einen bestimmten Satz von einem NICHT-Discord-Benutzer"""
    # Preventing problems with the length of the zitat and kontext because discords max embed description length is 4096
    if len(zitat) > 1500:
        await ctx.respond("Leider ist das Zitat zu lang (maximal `1500` Zeichen), bitte kürze es ein wenig", ephemeral=True)
        return
    if len(kontext) > 400:
        await ctx.respond("Leider ist der Kontext zu lang (maximal `400` Zeichen), bitte kürze ihn ein wenig", ephemeral=True)
        return
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{zitat}`\n{kontext if kontext == '' else f'({kontext})'}\n## @{benutzer.capitalize()}")
    zitat_embed.add_field(name="Rating", value="0", inline=False)
    zitat_embed.add_field(name="Zitiert von", value=f"{ctx.author.mention}", inline=False)
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url, text=f"{datetime.datetime.now().strftime('%d.%m.%Y | %H:%M')}")
    
    channel = bot.get_channel(settings.quotes_channel)
    message = await channel.send(embed=zitat_embed)
    await ctx.respond(f'**@{benutzer.capitalize()}** wurde mit folgendem Zitat zitiert: `{zitat}` von {ctx.author.mention}!', ephemeral=True)
    await message.add_reaction(f"<:{settings.upvote_emoji_name}:{settings.upvote_emoji_id}>")
    await message.add_reaction(f"<:{settings.downvote_emoji_name}:{settings.downvote_emoji_id}>")
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Inserting the quote into the database
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
                           Rating_User_IDs,
                           Zitat_Type
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                           (benutzer.capitalize(), 
                            ctx.author.display_name, 
                            0, 
                            ctx.author.id, 
                            zitat,
                            kontext, 
                            datetime.datetime.now().astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M"),
                            message.id,
                            0,
                            json.dumps([]),
                            1
                            ))
    conn.commit()
    conn.close()


@bot.message_command(guild_ids=guilds, name="Zitieren") # The App Integration for quoting discord messages
@commands.cooldown(1, settings.quote_cooldown, commands.BucketType.user)
@commands.has_role(settings.quote_permission_role)
async def app_zitat(ctx: discord.ApplicationContext, message):

    if len(message.content) > 1500:
        await ctx.respond("Leider ist die Nachricht zu lang (maximal `1500` Zeichen)", ephemeral=True)
        return
    zitat_embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## `{message.content}`\n({message.jump_url})\n## {message.author.mention}")
    zitat_embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
    zitat_embed.add_field(name="Rating", value="0", inline=False)
    zitat_embed.add_field(name="Zitiert von", value=f"{ctx.author.mention}", inline=False)
    zitat_embed.set_footer(icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url, text=f"{datetime.datetime.now().strftime('%d.%m.%Y | %H:%M')}")
    
    channel = bot.get_channel(settings.quotes_channel)
    new_message = await channel.send(embed=zitat_embed)
    await ctx.respond(f'Der Benutzer {message.author.mention} wurde mit folgendem Zitat zitiert: `{message.content}` von {ctx.author.mention}!', ephemeral=True)
    await message.add_reaction(f"<:{settings.upvote_emoji_name}:{settings.upvote_emoji_id}>")
    await message.add_reaction(f"<:{settings.downvote_emoji_name}:{settings.downvote_emoji_id}>")

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Inserting the quote into the database
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
                           Rating_User_IDs,
                           Zitat_Type
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                           (message.author.display_name, 
                            ctx.author.display_name, 
                            message.author.id, 
                            ctx.author.id, 
                            message.content,
                            '', 
                            datetime.datetime.now().astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M"),
                            new_message.id,
                            0,
                            json.dumps([]),
                            2
                            ))
    conn.commit()
    conn.close()

@bot.slash_command(guild_ids=guilds) # The Command for the fancy information text
@discord.default_permissions(administrator=True)
async def send_info_text(ctx):
    """Sendet den Info-Text"""
    allowed_mentions = discord.AllowedMentions(everyone=True, users=True, replied_user=True)
    info_embed = discord.Embed(
        color=discord.Color.from_rgb(209, 170, 212),
        description=f"""
            # Überarbeitung des Zitat-Systems
            \n### Das Zitatsystem wurde überarbeitet. Ab sofort können Nachrichten nur noch per Bot in den Zitatchannel gesendet werden.

            \n## Warum?
            \nUm Zitate übersichtlicher zu gestalten und das gesamte System zu vereinheitlichen. Außerdem hatten einige von euch Schwierigkeiten, die richtigen Zeichen zu finden oder das richtige Format zu benutzen.

            \n## Wie erstelle ich jetzt ein Zitat?
            \nZitate kannst du jetzt per Slash-Command erstellen. Nutze einfach `/zitat`, wähle den Nutzer aus, den du zitieren möchtest, und gib dann das Zitat ein. Anschließend kannst du entscheiden, ob du auch noch einen Kontext hinzufügen möchtest, der möglicherweise hilft, das Zitat besser zu verstehen. Zitate werden ab jetzt in einer Datenbank gespeichert und können somit auch schnell in einen anderen Kanal oder auf andere Plattformen übertragen werden. Zusätzlich gibt es den `/custom_zitat` Befehl, der genutzt wird, wenn die Person, die du zitieren möchtest, kein Discord-Benutzer ist oder sich nicht auf dem Server befindet. Dort trägst du dann den Namen in das Namensfeld ein, und die Namen werden automatisch groß- oder kleingeschrieben. Zum Beispiel wird aus "beRnd" "Bernd". Wenn du Discord-Nachrichten direkt in den Zitate-Channel stellen möchtest, kannst du dies einfach über einen `Rechtsklick -> Apps -> Zitieren` tun. Für das Zitieren gibt es einen Cooldown von `60 Sekunden`, aber der Bot informiert dich auch, wenn du noch warten musst.

            \n## Was ist das Rating?
            \nDas Rating ist ein neues System zur Bewertung von Zitaten. Dazu kannst du einfach die Pfeile unter einem Zitat verwenden, um das Zitat zu bewerten. Steigt der Score auf `10` oder höher, wird das Zitat angepinnt und ist leichter zu finden. Dadurch können die besten Zitate immer schnell und direkt gefunden werden. Fällt der Score eines Zitats auf oder unter `-3`, wird es sofort gelöscht und aus der Datenbank entfernt. Du kannst ein Zitat nur **einmal** positiv oder negativ bewerten, und die Bewertung kann **nicht** rückgängig gemacht werden. Die Bewertung ist anonym, es sei denn, jemand sieht genau in diesem Moment die Nachricht; deine Reaktion wird dann anschließend gelöscht.

            \n## Warum kann ich keine Unterhaltungen zitieren?
            \nDas Zitieren von Unterhaltungen ist aufgrund von Discord-spezifischen Einschränkungen mit dem neuen Format nicht mehr möglich. Daran kann ich leider auch nichts ändern. :c

            \n## Was passiert mit den bestehenden Zitaten?
            \nAlle bereits vorhandenen Zitate bleiben weiterhin im Channel erhalten; es handelt sich also nur um einen Formatwechsel. Allerdings werden alle bereits vorhandenen Zitate **nicht** in die Datenbank übernommen, d.h., sie gehen verloren, wenn sie auf eine andere Plattform übertragen werden. Dies liegt hauptsächlich an allen, die das Zitatformat nicht richtig eingehalten haben.

            \n## Ich kann die Commands nicht benutzen?
            \nStelle sicher das du die <@&{settings.quote_permission_role}> Rolle hast. Falls du sie nicht haben solltest, frag bitte einen der Admins ob er sie dir wieder gibt.
            
            \n## Mir gefällt Feature XY an dem Bot nicht?
            \nDu kannst gerne <@539142329546571806> kontaktieren und deine Idee einbringen. Alternativ kannst du auch gerne einen Pull-Request auf GitHub erstellen. \n[Link zum Repository](https://github.com/forest-cat/zitate).
            \n_ _
            """)
    info_embed.set_footer(icon_url=bot.user.avatar.url, text=f"{bot.user.display_name} am {datetime.datetime.now().strftime('%d.%m.%Y um %H:%M')}")
    info_msg = await ctx.send(embed=info_embed, allowed_mentions=allowed_mentions)
    await ctx.respond(f"Der Text wurde in {ctx.channel.mention} gesendet!", ephemeral=True)
    await info_msg.pin()

# running the actual bot
bot.run(settings.discord_token)