import os
import sys
import subprocess

try:
    import discord
    from discord.ext import commands
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py"])
    import discord
    from discord.ext import commands

TOKEN = 'your_discord_token'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
@commands.has_permissions(administrator=True)
async def now(ctx):
    guild = ctx.guild
    count = 0
    await ctx.send("جاري البدء...")
    for member in guild.members:
        if member != guild.owner and member != bot.user and not member.guild_permissions.administrator:
            try:
                await member.ban(reason="Clean")
                count += 1
            except: continue
    await ctx.send(f"تم حظر {count} عضو.")

if __name__ == '__main__':
    bot.run(TOKEN)
