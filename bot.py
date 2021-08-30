import discord
from discord.ext import commands
from discord.utils import get
from discord_components import Select, SelectOption, ComponentsBot
from plex_utils import Plex
from player import Player
import yaml
import logging


# set logging level
logging.basicConfig(level=logging.INFO)

#=======================================================
# get discord and plex configs from config.yml file
#=======================================================
configs = yaml.safe_load(open('./config.yml'))

DISCORD_TOKEN = configs['discord_token']
PLEX_SERVER = configs['plex_server']
PLEX_USER = configs['plex_user']
PLEX_PASSWORD = configs['plex_password']

# discord bot object
# bot = commands.Bot(command_prefix = '/')
bot = ComponentsBot("/")

# Plex object
plex = Plex(PLEX_SERVER, PLEX_USER, PLEX_PASSWORD)

# dict of player objects assigned to a channel
channel_players = {}

# dict storing the channel name
# and a list of songs to be played
song_queue = {}

def play_next_song(channel):
# get the next song in the channel song queue
    channel_name = channel.channel
    if len(song_queue[channel_name]) > 0:
        url = song_queue[channel_name].pop(0)
        logging.info(f'next_song: {url}')
        # play next song
        channel.play(discord.FFmpegOpusAudio(url), after=lambda e: play_next_song(channel))

@bot.event
async def on_ready():
    logging.info('It\'s alive!')
    
@bot.command(pass_context = True)
async def sandwich(ctx):
    await ctx.send('Cornbeef on Rye, coming right up!')

@bot.command(pass_context = True)
async def safeword(ctx):
    await ctx.send('Banana')

@bot.command(pass_context = True)
async def join(ctx):
    channel = ctx.message.author.voice.channel
    channel_name = channel.name

    channel_players[channel_name] = Player(channel)
    channel_players[channel_name].__str__()

    await channel.connect()

@bot.command(pass_context = True)
async def leave(ctx):
    source = ctx.message.author.voice.channel
    for channel in bot.voice_bots:
        if channel.channel == source:
            await channel.disconnect()

@bot.command(pass_context = True)
async def play(ctx, *, args):
    # get the channel the command came from
#    channel = get(bot.voice_bots, guild=ctx.guild)
#    channel_name = channel.channel

    # Search plex for artist
    artists = plex.get_artist(args)
    # Check if any artists were found
    if artists:
        # If more than one artist is found, send list of artists to pick from
        if len(artists) > 1:

            # Create a list of SelectOption objects
            select_options = []
            for index, artist in enumerate(artists):
                select_options.append(SelectOption(label=artist.title, value=artist.title))

            # Send the list of artists to pick from
            await ctx.send(
                "==== I found multiple artists ====", 
                components=[
                    Select(
                        placeholder="Select an artist",
                        options=select_options,
                        custom_id="select1",
                    ),
                ],
            )

            # Wait for a response            
            interaction = await bot.wait_for(
                "select_option", check=lambda inter: inter.custom_id == "select1"
            )
            await interaction.send(content=f"{interaction.values[0]} selected!", ephemeral=False)

            # Get the artist object
            for artist in artists:
                if artist.title == interaction.values[0]:
                    artists = artist

        # Search plex for albums by artist
        albums = plex.get_albums(artists)

        # If more than one album is found, send list of albums to pick from
        if len(albums) > 1:
            select_options = []
            for index, album in enumerate(albums):
                select_options.append(SelectOption(label=album.title, value=album.title))

            # Send the list of albums to pick from
            await ctx.send(
                "==== I found multiple albums ====", 
                components=[
                    Select(
                        placeholder="Select an album",
                        options=select_options,
                        custom_id="select1",
                    ),
                ],
            )
                        
            # Wait for a response            
            interaction = await bot.wait_for(
                "select_option", check=lambda inter: inter.custom_id == "select1"
            )
            await interaction.send(content=f"{interaction.values[0]} selected!", ephemeral=False)

            # Get the artist object
            for album in albums:
                if album.title == interaction.values[0]:
                    albums = album

        


@bot.command(pass_context = True)
async def pause(ctx):
    # get the channel the command came from
    source = ctx.message.author.voice.channel

    # of all the channels the bot is connected to,
    # find the one that matches the source of the command
    for channel in bot.voice_bots:
        if channel.channel == source:
            # get the player and pause the song
            channel.pause()

@bot.command(pass_context = True)
async def stop(ctx):
    # get the channel the command came from
    channel = get(bot.voice_bots, guild=ctx.guild)
    channel_name = channel.channel

    # stop playback
    channel.stop()

@bot.command(pass_context = True)
async def resume(ctx):
    # get the channel the command came from
    source = ctx.message.author.voice.channel

    # of all the channels the bot is connected to,
    # find the one that matches the source of the command
    for channel in bot.voice_bots:
        if channel.channel == source:
            # get the player and resume the song
            channel.resume()

#=========================
# Run the discord bot
#=========================
bot.run(DISCORD_TOKEN)
