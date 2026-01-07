import json
import logging
import sqlite3

import requests
from discord.ext import commands
from config import load_config
from discord.commands import slash_command


settings = load_config()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(settings.log_format))
logger = logging.getLogger('app.cogs.events')
logger.setLevel(settings.log_level)
logger.addHandler(handler)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Logged in as: \033[36m{self.bot.user.name}\033[90m#\033[37m{self.bot.user.discriminator}\033[0m")
        conn = sqlite3.connect(settings.db_filename)
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


    # Handling the Rating System over the Reactions
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.member == self.bot.user:
            return
        if reaction.emoji.id not in [settings.upvote_emoji_id, settings.downvote_emoji_id]:
            return

        # Searching if the message is in the database
        conn = sqlite3.connect(settings.db_filename)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Zitate WHERE Message_ID = ?", (reaction.message_id,))
        rows = cursor.fetchall()
        if len(rows) < 1:
            return
        row = rows[0]

        channel = self.bot.get_channel(settings.quotes_channel)
        message = await channel.fetch_message(reaction.message_id)
        embed = message.embeds[0]
        await message.remove_reaction(reaction.emoji, reaction.member)

        if reaction.emoji.id == settings.upvote_emoji_id:  # Handling if the user upvotes a quote
            json_obj = json.loads(row[10])
            rating = int(row[9]) + 1
            if reaction.member.id not in json.loads(row[10]):
                json_obj.append(reaction.member.id)
                cursor.execute("UPDATE Zitate SET Rating = ?, Rating_User_IDs = ? WHERE Message_ID = ?",
                               (rating, json.dumps(json_obj), reaction.message_id))
                conn.commit()
                embed.fields[0].value = str(rating)
                await message.edit(embed=embed)
            else:
                await reaction.member.send(
                    f"Du hast bereits für dieses Zitat (https://discord.com/channels/{reaction.guild_id}/{reaction.channel_id}/{reaction.message_id}) gevotet!")
            if rating >= 10:  # Pinning the quote if the rating is 5 or higher
                await message.pin()
        elif reaction.emoji.id == settings.downvote_emoji_id:  # Handling if the user downvotes a quote
            json_obj = json.loads(row[10])
            rating = int(row[9]) - 1
            if reaction.member.id not in json.loads(row[10]):
                json_obj.append(reaction.member.id)
                cursor.execute("UPDATE Zitate SET Rating = ?, Rating_User_IDs = ? WHERE Message_ID = ?",
                               (rating, json.dumps(json_obj), reaction.message_id))
                conn.commit()
                embed.fields[0].value = str(rating)
                await message.edit(embed=embed)
            else:
                await reaction.member.send(
                    f"Du hast bereits für dieses Zitat (https://discord.com/channels/{reaction.guild_id}/{reaction.channel_id}/{reaction.message_id}) gevotet!")
            if rating <= -3:  # Deleting the quote if the rating is -3 or lower
                await message.delete()
                cursor.execute("DELETE FROM Zitate WHERE Message_ID = ?", (reaction.message_id,))
                conn.commit()


    # Catching specific errors from the slash commands
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.respond(f"Bitte warte noch `{round(error.retry_after, 1)} Sekunden` und probiere es dann erneut",
                              ephemeral=True)
        elif isinstance(error, commands.errors.MissingRole):
            await ctx.respond(f"Dir fehlt dazu leider die <@&{settings.quote_permission_role}> Rolle", ephemeral=True)
        elif isinstance(error, requests.exceptions.RequestException):
            await ctx.respond(f"Es gab einen Fehler in der Kommunikation mit der SIS-API", ephemeral=True)
        else:
            raise error

def setup(bot):
    bot.add_cog(Events(bot))