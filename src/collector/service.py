from src.app.gateways.artist_store import ArtistStore
from src.app.gateways.release_store import ReleaseStore
from src.app.gateways.review_store import ReviewStore
from src.collector.web import metacritic, aoty

from constants import METACRITIC_CURATED_PUBLICATIONS, METACRITIC_PUBLICATIONS_SAMPLE, AOTY_CURATED_PUBLICATIONS, AOTY_PUBLICATIONS_SAMPLE
from src.app.db.file_adapter import FileAdapter


class CollectorService:

    def __init__(self, music_cataloger, enricher):
        self.music_cataloger = music_cataloger
        self.review_store = ReviewStore(FileAdapter('reviews'))
        self.release_store = ReleaseStore(FileAdapter('releases'), self.review_store)
        self.artist_store = ArtistStore(FileAdapter('artists'), ReleaseStore(FileAdapter('releases'), self.review_store))
        self.enricher = enricher

    def collect_reviews(self):

        # TODO: the term "collect" is perhaps a bit overloaded. We describe the overall job of the service of going off
        #  to the internet and storing new reviews collecting and we call the controllers that physically fetch the data
        #  collectors as well
        self.music_cataloger.collect_reviews(metacritic, publications=METACRITIC_PUBLICATIONS_SAMPLE)
        self.music_cataloger.collect_reviews(aoty, publications=AOTY_PUBLICATIONS_SAMPLE)
        recently_reviewed_artists = self.music_cataloger.catalog_reviews()

        archived_artists = self.artist_store.get_all()
        # archive_copy = archived_artists.copy()
        # known_artists = archive_copy.update(recently_reviewed_artists)
        known_artists = dict(archived_artists, **recently_reviewed_artists)
        print('enriching release data')

        enriched_artists = self.enricher.add_release_dates(known_artists)

        self.artist_store.put(enriched_artists)
        self.release_store.put(enriched_artists)
