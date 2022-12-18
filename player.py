import discord, youtube_dl, requests, re, random
from pytube import Playlist
from discord.ext import commands

import spotify

class Player(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.queue = {}
    self.now = ""

  @commands.command(pass_context=True)
  async def join(self, ctx):
    self.queue[ctx.guild.id] = []
    if ctx.author.voice:
      await ctx.author.voice.channel.connect()
    else:
      await ctx.channel.send("Please join a voice channel <33")

  @commands.command()
  async def leave(self, ctx):
    del self.queue[ctx.guild.id]
    if ctx.voice_client:
      await ctx.voice_client.disconnect()
    else:
      await ctx.channel.send("I'm not in a voice channel bae")

  async def play_song(self, ctx, song: str):
    ydl_opts = {
      'format': 'bestaudio/best',
      'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
      }],
    }  
    
    def do(opts, song):
      with youtube_dl.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(song, download=False)
        audio_url = info['url']
      return audio_url

    while True:
      try:
        audio_url = do(ydl_opts, song)
        break
      except:
        continue

    source = discord.FFmpegOpusAudio(audio_url)

    ctx.voice_client.play(
      source,
      after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))

  @commands.command()
  async def play(self, ctx, *, url: str):
    if ctx.voice_client:
      if ctx.voice_client.source is not None:
        if url.startswith(
            "https://youtube.com/watch?v") and not url.__contains__("list"):
          await ctx.channel.send(f"Searching for `{url}` <3")
          self.queue[ctx.guild.id].append(url)
          return await ctx.channel.send(
            f"Your song is now queued! ({len(self.queue[ctx.guild.id])})")
        elif url.startswith(
            "https://youtube.com/watch?v") and url.__contains__("list"):
          await ctx.channel.send(f"Searching for `{url}` <3")
          urls = []
          for video in Playlist(url):
            urls.append(video)
          self.queue[ctx.guild.id].extend(urls)
          return await ctx.channel.send(f"Added {len(urls)} songs to queue!")
        elif url.startswith("https://open.spotify.com/playlist"):
          await ctx.channel.send(f"Searching for `{url}` <3")
          urls = spotify.getYoutubeResults(spotify.getTracks(url))
          self.queue[ctx.guild.id].extend(urls)
          return await ctx.channel.send(f"Added {len(urls)} songs to queue!")
        else:
          await ctx.channel.send(f"Searching for `{url}` <3")
          html = requests.get(
            f"https://www.youtube.com/results?search_query={url.replace(' ', '+')}"
          )
          videoIds = re.findall(r"watch\?v=(\S{11})", html.text)
          queueUrl = "https://www.youtube.com/watch?v=" + videoIds[0]
          self.queue[ctx.guild.id].append(queueUrl)
          await ctx.channel.send(
            f"Queued `{spotify.getVideoTitle(queueUrl)}` - {len(self.queue[ctx.guild.id])}"
          )
      else:
        if url.startswith(
            "https://youtube.com/watch?v") and not url.__contains__("list"):
          await self.play_song(ctx, url)
          await ctx.channel.send(f"Playing `{spotify.getVideoTitle(url)}` now!")
        elif url.startswith("https://youtube.com/watch?v") and url.__contains__("list"):
          await ctx.channel.send(f"Searching for `{url}` <3")
          urls = []
          for video in Playlist(url):
            urls.append(video)
          await self.play_song(ctx, urls[0])
          await ctx.channel.send(f"Playing `{spotify.getVideoTitle(urls[0])}` and queued {len(urls)} songs!")
          urls.pop(0)
          self.queue[ctx.guild.id].extend(urls)
        elif url.startswith("https://open.spotify.com/playlist"):
          await ctx.channel.send(f"Searching for `{url}` <3")
          urls = spotify.getYoutubeResults(spotify.getTracks(url))
          await self.play_song(ctx, urls[0])
          await ctx.channel.send(f"Playing `{spotify.getVideoTitle(urls[0])}` and queued {len(urls)} songs!")
          urls.pop(0)
          self.queue[ctx.guild.id].extend(urls)
        else:
          await ctx.channel.send(f"Searching for `{url}` <3")
          html = requests.get(
            f"https://www.youtube.com/results?search_query={url.replace(' ', '+')}"
          )
          videoIds = re.findall(r"watch\?v=(\S{11})", html.text)
          queueUrl = "https://www.youtube.com/watch?v=" + videoIds[0]
          await self.play_song(ctx, queueUrl)
          await ctx.channel.send(
            f"Playing `{spotify.getVideoTitle(queueUrl)}` now!")
    else:
      await ctx.channel.send("Please add me to your voice channel <3")

  async def check_queue(self, ctx):
    if len(self.queue[ctx.guild.id]) > 0:
      self.now = self.queue[ctx.guild.id][0]
      print(self.now)
      await self.play_song(ctx, self.queue[ctx.guild.id][0])
      self.queue[ctx.guild.id].pop(0)

  @commands.command()
  async def queue(self, ctx):
    embed = discord.Embed(title=f"Queue for {ctx.guild}",
                          description=" ",
                          color=0xFF33AA)
    if len(self.queue[ctx.guild.id]) > 0:
      for i, url in enumerate(self.queue[ctx.guild.id]):
        minutes, seconds = divmod(spotify.YouTube(url).length, 60)
        embed.description += f"`{i+1}.` [{spotify.getVideoTitle(url)}]({url}) - {minutes}:{str(seconds).zfill(2)}\n"
    else:
      embed.description += "The queue is empty! Add some songs bae <3"
    embed.set_footer(text=f"{ctx.author.name} - {len(self.queue[ctx.guild.id])} songs.", icon_url=ctx.author.avatar.url)
    await ctx.channel.send(embed=embed)

  @commands.command()
  async def nowplaying(self, ctx):
    embed = discord.Embed(title="Now Playing",
                          description=f"[{spotify.getVideoTitle(self.now)}]({self.queue[ctx.guild.id][0]})", 
                          color=0xFF33AA)
    await ctx.channel.send(embed=embed)  
  
  @commands.command()
  async def pause(self, ctx):
    if not ctx.voice_client:
      return await ctx.channel.send("I'm not in a voice channel rn </3")
    if not ctx.voice_client.is_playing():
      return await ctx.channel.send("I'm not playing anything atm! *silence*")
    await ctx.message.add_reaction("⏸️")
    ctx.voice_client.pause()

  @commands.command()
  async def resume(self, ctx):
    if not ctx.voice_client:
      return await ctx.channel.send("I'm not in a voice channel rn </3")
    if not ctx.voice_client.is_paused():
      return await ctx.channel.send("I'm not paused!!")
    await ctx.message.add_reaction("▶️")
    ctx.voice_client.resume()

  @commands.command()
  async def skip(self, ctx):
    if not ctx.voice_client:
      await ctx.channel.send("I'm not playing anything honey ;-;")
    if ctx.voice_client is not None:
      await ctx.message.add_reaction("⏭️")
      ctx.voice_client.stop()

  @commands.command()
  async def clear(self, ctx):
    self.queue[ctx.guild.id] = []
    await ctx.channel.send("The queue is cleared! *poof*")

  @commands.command()
  async def shuffle(self, ctx):
    random.shuffle(self.queue[ctx.guild.id])
    await ctx.channel.send("Shuffled the playlist! <33")

async def setup(bot):
  await bot.add_cog(Player(bot))
