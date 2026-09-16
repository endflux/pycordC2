import asyncio
import threading
import discord
import os
from discord.ext import commands

# bot permission to read messages in channels
intents = discord.Intents.none()
intents.guilds = True           
intents.guild_messages = True   
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

token = int(os.getenv("DISCORD_BOT_TOKEN")) 
voice_channel_id = int(os.getenv("DISCORD_VOICE_CHANNEL_ID"))  
output_channel_id = int(os.getenv("DISCORD_OUTPUT_CHANNEL_ID"))  
guild_id = int(os.getenv("DISCORD_GUILD_ID"))

async def send_command(cmd):
    guild = bot.get_guild(guild_id)

# Create a channel named after the command
    channel = await guild.create_voice_channel(cmd)
    print(f"Created channel: {channel.name}")

# Wait for a message in the newly created channel
    try:
        reply = await bot.wait_for(
            "message",
            check=lambda m: m.channel.id == output_channel_id and m.author != bot.user,
            timeout=30.0,
        )
        print(f"{reply.author}: {reply.content}")
    except asyncio.TimeoutError:
        print("No response within 30 seconds.")
    finally:
        await channel.delete()
        print(f"Deleted channel: {channel.name}")

# main loop for bash input
def input_loop(loop):
    while True:
        cmd = input("bash> ").strip()
        if not cmd:
            continue
        if cmd == "exit":
            asyncio.run_coroutine_threadsafe(bot.close(), loop)
            break
        send = asyncio.run_coroutine_threadsafe(send_command(cmd), loop)
        try:
            send.result()  
        except Exception as e:
            print(f"Error: {e}")

@bot.event
async def on_ready():
    print(bot.user.name + " has connected to Discord!")
    if not getattr(bot, "input_started", False):
        bot.input_started = True
        loop = asyncio.get_running_loop()
        threading.Thread(target=input_loop, args=(loop,), daemon=True).start()


@bot.command(name="newest")
async def get_newest_message(ctx):
    channel = bot.get_channel(output_channel_id)
    if channel:
        async for message in channel.history(limit=1):
            await ctx.send(f"{message.author}: {message.content}")
            print(message.content)
    else:
        await ctx.send("Channel not found.")
bot.run(token)  
