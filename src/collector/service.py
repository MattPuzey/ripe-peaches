from src.app.gateways.artist_store import ArtistStore
from src.app.gateways.release_store import ReleaseStore
from src.app.gateways.review_store import ReviewStore
from src.collector.web import metacritic, aoty, spotify

from constants import METACRITIC_PUBLICATIONS_SAMPLE, AOTY_PUBLICATIONS_SAMPLE
from src.app.db.file_adapter import FileAdapter


class CollectorService:

    def __init__(self, review_collector, release_collector):
        self.review_collector = review_collector
        self.release_collector = release_collector
        self.review_store = ReviewStore(FileAdapter('reviews'))
        self.release_store = ReleaseStore(FileAdapter('releases'), self.review_store)
        self.artist_store = ArtistStore(FileAdapter('artists'))

    def collect_reviews(self):

        self.review_collector.collect(metacritic, publications=METACRITIC_PUBLICATIONS_SAMPLE)
        self.review_collector.collect(aoty, publications=AOTY_PUBLICATIONS_SAMPLE)
        artists = self.review_collector.catalog()

        self.artist_store.put(artists)
        self.release_store.put(artists)

    def collect_releases(self):

        self.release_collector.collect(spotify)
        artists = self.release_collector.catalog()

        self.artist_store.put(artists)
        self.release_store.put(artists)
