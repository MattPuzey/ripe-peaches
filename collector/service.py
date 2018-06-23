from collector.review_scraper import ReviewsScraper
from app.storage.review_store import ReviewStore


class CollectorService:

    @staticmethod
    def start():
        store = ReviewStore()
        scraper = ReviewsScraper()
        harvested_data = scraper.collect()
        store.store_reviews(harvested_data)
