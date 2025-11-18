from scrapy.exceptions import DropItem

class ItemCollector:
    """
    Pipeline Scrapy pour collecter les items dans une liste passée via les settings.
    """
    def __init__(self, settings):
        # Récupérer la liste passée via les settings
        self.items = settings.get('RAW_DATA_LIST', [])
        if self.items is None:
            raise ValueError("RAW_DATA_LIST n'a pas été passé aux settings du pipeline.")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        # Ajouter l'item à la liste
        self.items.append(dict(item))
        return item
