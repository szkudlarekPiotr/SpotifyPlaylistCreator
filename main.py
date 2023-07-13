import requests
from requests.exceptions import HTTPError, InvalidSchema, ConnectionError
import datetime
from bs4 import BeautifulSoup
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys

print("------------MUSICAL TIME MACHINE--------------")

date_format = "%Y-%m-%d"
bilboard_url = "https://www.billboard.com/charts/hot-100/"

try:
    user_input = input("Which year do you want to travel to? (YYYY-MM-DD):")
    date = str(datetime.datetime.strptime(user_input, date_format).date())
    year = int(date.split("-")[0])
except ValueError:
    print("Please input correct date")

try:
    response = requests.get(url=f"{bilboard_url}{date}")
    response.raise_for_status()
except (HTTPError, InvalidSchema, ConnectionError) as e:
    print(f"Invalid request: {e.args}")

soup = BeautifulSoup(response.text, "html.parser")

all_titles = soup.find_all(
    class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only"
)

first_title = soup.find(
    class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet"
)

all_artists = soup.find_all(
    class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only"
)

first_artist = soup.find(
    class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only u-font-size-20@tablet"
)

if all_titles and first_title:
    title_list_formatted = [re.sub("\s+", "", str(tag.text)) for tag in all_titles]
    first_title_formatted = re.sub("\s+", "", str(first_title.text))
    title_list_formatted.insert(0, first_title_formatted)
else:
    print("Tracks not found")
    sys.exit(1)

if all_artists and first_artist:
    artist_list_formated = [re.sub("\s+", "", str(tag.text)) for tag in all_artists]
    first_artist_formatted = re.sub("\s+", "", str(first_artist.text))
    artist_list_formated.insert(0, first_artist_formatted)
else:
    print("Artists not found")
    sys.exit(1)

combined_list = [list(item) for item in zip(title_list_formatted, artist_list_formated)]

access_scope = "playlist-modify-private playlist-read-private"

spotify = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        cache_path="token.txt",
        scope=access_scope,
    )
)

user_id = spotify.current_user()["id"]

spotify.user_playlist_create(user=user_id, name=f"BILBOARD {date}", public=False)

user_playlists = spotify.user_playlists(user=user_id)

for item in user_playlists["items"]:
    if item["name"] == f"BILBOARD {date}":
        playlist_id = item["id"]
        break
    else:
        print("Playlist not found")
        sys.exit(1)

tracks_id = []

for item in combined_list:
    query = f"{item[1]} {item[0]} {str(year-20)}-{str(year+1)}"
    search_result = spotify.search(q=query, type="track", limit=1, market="US")
    try:
        song_id = search_result["tracks"]["items"][0]["id"]
        tracks_id.append(f"spotify:track:{song_id}")
    except IndexError as e:
        print(f"Song not found {item[1]}, {item[0]}")


spotify.playlist_add_items(playlist_id=playlist_id, items=tracks_id)
