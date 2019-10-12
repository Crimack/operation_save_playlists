# Operation Save Playlists

## Why?

After I imported my iTunes playlists to Spotify, half of them were broken. The 
URIs would be something like `spotify:local:......`, which meant they were only playable 
on a computer I no longer have. I wanted to resurrect some playlists that are only on my iPod.

Goals:
* Fix all old playlists
* Back everything up before modifying it
* Try to fix them as automatically as possible
* Don't make big assumptions. I'd rather have less tracks than incorrect tracks

I say 'As automatically as possible' because song catalogs are hard. Songs tend to have different names
and formats e.g. does the featured artist go in the song title or the artists column?. Also, 
sometimes either you or Spotify just has incorrect metadata. Or you have some weird bootleg 
live versions that aren't streamable. The scripts use some hardcoded transformations (located 
in `transformations.txt`), and also make some assumptions. Sometimes it's too hard to automagically 
work it out (e.g. when unpacking Greatest Hits albums), and the scripts will just prompt for help:

[![Image from Gyazo](https://i.gyazo.com/ef64a583854f264a4dd17dda7d59be74.gif)](https://gyazo.com/ef64a583854f264a4dd17dda7d59be74)

## Usage
1. `pipenv install`
2. Spotipy expects a client ID and client secret to be available as environment 
variables. Also add an environment variable SPOTIPY_REDIRECT_URI with the value 
of http://localhost/, which will authenticate the app.
3. Copy/modify `whitelist.txt` to contain the names of playlists you want to fix
4. Run `get_playlist.py` with your username and the name of your whitelist file to fetch 
    metadata about the playlists you want to fix
5. Run `fix_playlists.py` with your username to run the fixer.
6. Listen to the resurrected forms of your carefully curated playlists with glee
