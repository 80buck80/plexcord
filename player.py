# manage songs being played by the plexcord bot


class Player():

    def __init__(self, channel):
        self.channel = channel
        self.song_queue = {}

    def __str__(self):
        print (self.channel.name)
