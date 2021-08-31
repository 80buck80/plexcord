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
bot = ComponentsBot("/")
# remove default help command
bot.remove_command('help')

# Plex object
plex = Plex(PLEX_SERVER, PLEX_USER, PLEX_PASSWORD)

# dict of player objects assigned to a channel
channel_players = {}

# dict storing the channel name
# and a list of songs to be played
song_queue = {}

def play_next_song(channel):
# get the next song in the channel song queue
    #channel_name = channel.channel
    #voice = get(bot.voice_clients, guild=ctx.guild)
    channel_name = channel.channel.name

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
    await ctx.send("Type /help for options")

@bot.command(pass_context = True)
async def help(ctx):
    # Print out a list of options
    embed = discord.Embed(color = discord.Color.blue())

    embed.set_author(name="Plexbot 2.0\n")

    embed.add_field(name="/play <artist>", value="Searches for and plays artist", inline=False)
    embed.add_field(name="/search <artist>", value="Prints a list of available artists", inline=False)
    embed.add_field(name="/stop", value="Stops playback", inline=False)
    embed.add_field(name="/resume", value="Resumes playback", inline=False)
    embed.add_field(name="/next", value="Plays the next song", inline=False)
    embed.add_field(name="/leave", value="Disconnects the bot", inline=False)

    await ctx.send(embed=embed)

@bot.command(pass_context = True)
async def leave(ctx):
    # Disconnect the bot from the voice channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    await voice.disconnect()

@bot.command(pass_context = True)
async def play(ctx, *, args):
    # get the channel the command came from
    channel = ctx.message.author.voice.channel
    channel_name = channel.name
    voice = get(bot.voice_clients, guild=ctx.guild)

    # If the bot is currently playing, pause it
    if voice.is_playing():
        voice.pause()

    if args.lower() == "the":
        await ctx.send(f"{args} is too vague")

    elif args.lower() == "random":
        await ctx.send(f"Someday there will be a random function")
    else:    
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
                for a in artists:
                    if a.title == interaction.values[0]:
                        artist = a
            else:
                # Set artist to the one found artist object
                artist = artists[0]

            # Search plex for albums by artist
            albums = plex.get_albums(artist)

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
                for a in albums:
                    if a.title == interaction.values[0]:
                        album = a
            else:
                # Set album to the one found album object
                album = albums[0]

            # Get a list of album tracks
            tracks = plex.get_album_track_urls(album)            

            # Add the songs to the channel's queue
            song_queue[channel_name] = tracks

            # Play songs in the channel queue
            play_next_song(voice)

        else:
            await ctx.send(f"I could not find a match for {args}")

        
@bot.command(pass_context = True)
async def stop(ctx):
    # get the channel the command came from
    voice = get(bot.voice_clients, guild=ctx.guild)
    source = ctx.message.author.voice.channel

    voice.pause()

@bot.command(pass_context = True)
async def next(ctx):
    # get the channel the command came from
    voice = get(bot.voice_clients, guild=ctx.guild)
    channel_name = voice.channel.name

    # stop playback
    voice.stop()

@bot.command(pass_context = True)
async def resume(ctx):
    # get the channel the command came from
    voice = get(bot.voice_clients, guild=ctx.guild)
    channel_name = voice.channel.name

    voice.resume()

@bot.command(pass_context = True)
async def search(ctx, *, args):
    # Searches for and prints out a list of artists
    results = plex.get_artist(args)
    for artist in results:
        await ctx.send(artist.title)

    


#=========================
# Run the discord bot
#=========================
bot.run(DISCORD_TOKEN)
