import discord
from discord.ext import commands
from discord.utils import get
from plex_utils import Plex



TOKEN = 'NzM0MDk1ODQxNzE4OTYwMTQ5.XxMuBw.0_UMkHua0b3h8eWpFYnEva3TnK4'

# discord client object
client = commands.Bot(command_prefix = '/')

# Plex object
plex = Plex()

# dict storing the channel name
# and a list of songs to be played
song_queue = {}

def play_next_song(ctx):
# get the next song in the channel song queue
    channel = get(client.voice_clients, guild=ctx.guild)
    channel_name = channel.channel
    if len(song_queue[channel_name]) > 0:
        url = song_queue[channel_name].pop(0)
        print(f'next_song: {url}')
        # play next song
        channel.play(discord.FFmpegOpusAudio(url), after=lambda e: play_next_song(ctx))

@client.event
async def on_ready():
    print('It\'s alive!')

@client.command(pass_context = True)
async def sandwich(ctx):
    await ctx.send('Cornbeef on Rye, comming right up!')

@client.command(pass_context = True)
async def safeword(ctx):
    await ctx.send('Banana')

@client.command(pass_context = True)
async def what(ctx):
    await ctx.send(ctx.channel)

@client.command(pass_context = True)
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()

@client.command(pass_context = True)
async def leave(ctx):
    source = ctx.message.author.voice.channel
    for channel in client.voice_clients:
        if channel.channel == source:
            await channel.disconnect()

@client.command(pass_context = True)
async def play(ctx):
    # get the channel the command came from
    source = ctx.message.author.voice.channel

    # of all the channels the bot is connected to,
    # find the one that matches the source of the command
    for channel in client.voice_clients:
        if channel.channel == source:
            # song_arr = []
            #
            # for url in urls:
            #     print (url)
            #     # get song url from plex
            #     song = await discord.FFmpegOpusAudio.from_probe(url)
            #     # store the song in an array
            #     song_arr.append(song)

            # add channel id and song array to the queue

            # song = get_next_song(channel.channel)

            tracks = plex.get_all_artist_track_urls('berry')

            channel_name = channel.channel
            song_queue[channel_name] = tracks

            url = song_queue[channel_name].pop(0)
            # song = await discord.FFmpegOpusAudio.from_probe(url)
            # print (song)
            # play next song
            # channel.play(song, after=lambda e: play_next_song(ctx))
            channel.play(discord.FFmpegOpusAudio(url), after=lambda e: play_next_song(ctx))

@client.command(pass_context = True)
async def pause(ctx):
    # get the channel the command came from
    source = ctx.message.author.voice.channel

    # of all the channels the bot is connected to,
    # find the one that matches the source of the command
    for channel in client.voice_clients:
        if channel.channel == source:
            # get the player and pause the song
            channel.pause()

@client.command(pass_context = True)
async def stop(ctx):
    # get the channel the command came from
    source = ctx.message.author.voice.channel

    # of all the channels the bot is connected to,
    # find the one that matches the source of the command
    for channel in client.voice_clients:
        if channel.channel == source:
            # get the player and stop the song
            channel.stop()

@client.command(pass_context = True)
async def resume(ctx):
    # get the channel the command came from
    source = ctx.message.author.voice.channel

    # of all the channels the bot is connected to,
    # find the one that matches the source of the command
    for channel in client.voice_clients:
        if channel.channel == source:
            # get the player and resume the song
            channel.resume()








client.run(TOKEN)
