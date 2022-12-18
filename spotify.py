import re, spotipy, requests
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube

auth_manager = SpotifyClientCredentials('4578e393effc4e8d8cc95e2d11ed8b5d',
                                        '197465f1ea61487482ea5073918ad809')
sp = spotipy.Spotify(auth_manager=auth_manager)
    
def getUri(link):
    return link.split("/")[-1].split("?")[0]

def getTracks(link):
    meta = []
    for track in sp.playlist_tracks(getUri(link))['items']:
        meta.append([track["track"]["name"], track["track"]["album"]["artists"][0]["name"]])
    return meta

def getVideoTitle(link):
    return YouTube(link).title

def getYoutubeResults(tracks):
    urls = []
    for i in range(len(tracks)):
        html = requests.get(f"https://www.youtube.com/results?search_query={tracks[i][0]}+{tracks[i][1]}")
        videoIds = re.findall(r"watch\?v=(\S{11})", html.text)
        videoUrl = "https://www.youtube.com/watch?v=" + videoIds[0]
        urls.append(videoUrl)
    return urls