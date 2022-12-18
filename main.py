import discord, asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def load_extensions():
    await bot.load_extension("player")

asyncio.run(load_extensions())

@bot.event
async def on_ready():
    print('Ready <3')
    
@bot.command()
async def purge(ctx, num: int):
    await ctx.channel.purge(limit=num)
    
@bot.command()
async def ping(ctx):
    await ctx.channel.send(f"Latency: {round(bot.latency*1000)}ms")

bot.run('ODE1MjE0NDMyMDA3MDk0Mjgy.GFGyaS.HZjdXILALdVtCFRY67teqzInKgqNNJ2yRmRZ9o')