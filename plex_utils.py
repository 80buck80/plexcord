'''
musicLib = plex.library.section('Music')
tool = musicLib.search(title='Tool')
albums = tool[0].albums()
tracks = tool[0].tracks()

 tracks[0].grandparentTitle
'The Flaming Lips'
>>> tracks[0].parentTitle
'Embryonic'
>>> tracks[0].title
'Convinced of the Hex'


tracks[0].getStreamURL()
'https://192-168-0-107.cee942202f6a4709abbd590517a43eae.plex.direct:32400/audio/:/transcode/universal/start.m3u8?X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&offset=0&path=%2Flibrary%2Fmetadata%2F6949&X-Plex-Token=8PQHxAPkkGgPg4d--3xq'
'''

from plexapi.myplex import MyPlexAccount
from plexapi.library import LibrarySection

class Plex():
    def __init__(self, server, user, password):
        self.account = MyPlexAccount(user, password)
        self.plex = self.account.resource(server).connect()
        self.library = self.plex.library.section('Music')

    def get_all_artists(self):
        # Return a list of all artists in the Plex Music Library
        return self.library.all()

    def get_artist(self, artist):
        # user artist arg to search library for an artist
        # search returns a list of artist objects.
        search = self.library.searchArtists(title=f'{artist}')
        if search:
            return search
        else:
            return False

    def get_albums(self, artist):
        # use artist object to get all artist albums
        # return a list of album objects
        
        # search for the artist
        search = artist.albums()
        if search:
            return search
        else:
            return False    

    def get_album_track_urls(self, album):
        # use album object to get all tracks from an artist's albums
        # return a list of track urls

        tracks = album.tracks()
        urls = []
        for track in tracks:
            urls.append(track.getStreamURL()) 
    
        return urls
        
    def get_all_artist_track_urls(self, artist):
        # use artist object to get all tracks from an artist's albums
        # return a list of urls to the tracks

        # search for the artist
        artist = self.get_artist(artist)
        if artist:
            tracks = artist.tracks()
            urls = []
            for track in tracks:
                urls.append(track.getStreamURL())
        else:
            return False

        if urls:
            return urls
        else:
            return False
