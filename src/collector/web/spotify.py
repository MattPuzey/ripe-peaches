import os
from urllib import parse
import json
import base64
import requests
import constants
import string

from src.collector.entities.external_release import ExternalRelease


class Spotify:

    def __init__(self):
        self.access_token = self._get_access_token()

    @staticmethod
    def _get_access_token():

        client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        client_details = '%s:%s' % (client_id, client_secret)
        encoded_client_details = base64.b64encode(client_details.encode('utf-8')).decode('utf-8')
        details = 'Basic %s' % encoded_client_details

        authorization_response = requests.post('https://accounts.spotify.com/api/token',
                                               data={'grant_type': 'client_credentials'},
                                               headers={'Authorization': details})

        access_token = json.loads(authorization_response.text).get('access_token')

        return access_token

    def get_release_details(self, artist_name, album_name) -> ExternalRelease:

        spotify_search = f'https://api.spotify.com/v1/search?type=album&q=album:"{album_name}"+artist:"{artist_name}"'
        response = requests.get(spotify_search, headers={'Authorization': 'Bearer %s' % self._get_access_token()}).json()

        spotify_album = None
        for album in response['albums']['items']:
            if album['name'].lower() == album_name.lower():
                spotify_album = album
                break

        if not spotify_album:
            return ExternalRelease(name=artist_name, artist=artist_name)

        release_date = spotify_album.get('release_date')
        album_type = spotify_album.get('album_type')
        total_tracks = spotify_album.get('total_tracks')
        external_urls = spotify_album.get('external_urls')
        spotify_url = None
        if external_urls:
            spotify_url = external_urls.get('spotify')

        return ExternalRelease(
            name=artist_name,
            artist=artist_name,
            date=release_date,
            type=album_type,
            total_tracks=total_tracks,
            spotify_url=spotify_url
        )

    def get_releases(self) -> [ExternalRelease]:
        print('Fetching recent releases from Spotify...')

        external_releases = []
        wildcard_chars = list(string.ascii_lowercase)
        for char in wildcard_chars:
            next_page = constants.SPOTIFY_NEW_RELEASE_SEARCH.format(char=char)
            while next_page:
                offset = dict(parse.parse_qsl(parse.urlsplit(next_page).query)).get('offset', 0)
                if int(offset) >= 10000:
                    break
                response = requests.get(next_page, headers={'Authorization': 'Bearer %s' % self._get_access_token()}).json()
                new_items, next_page = self._parse_response(response)
                if new_items:
                    external_releases.extend(new_items)

        return self._parse_releases(external_releases)

    @staticmethod
    def _parse_response(response):

        albums = response.get('albums')

        if not albums:
            return None, None

        items = albums.get('items')
        valid_items = [item for item in items if item]

        return valid_items, albums.get('next')

    @staticmethod
    def _parse_releases(external_releases) -> [ExternalRelease]:

        releases = []
        for external_release in external_releases:
            release = ExternalRelease(
                name=external_release.get('name'),
                artist=external_release.get('artists')[0].get('name'),
                date=external_release.get('release_date'),
                type=external_release.get('type'),
                spotify_url=external_release.get('external_urls').get('spotify'),
                total_tracks=external_release.get('total_tracks')
            )
            releases.append(release)

        print('Finished fetching recent releases from Spotify')
        return releases
