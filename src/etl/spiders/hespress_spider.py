import scrapy
from datetime import datetime, timezone

class HespressSpider(scrapy.Spider):
    name = "hespress_pep_spider"
    allowed_domains = ["fr.hespress.com"]
    start_urls = [
        "https://fr.hespress.com/politique",
        "https://fr.hespress.com/economie"
    ]
    
    # Poids de la source pour le calcul du score de confiance
    source_weight = 0.2
    source_type = "media"

    def parse(self, response):
        # Sélecteur pour les liens d'articles sur la page d'index
        # J'utilise un sélecteur générique pour les articles sur la page
        article_links = response.css('div.article-card a::attr(href)').getall()
        
        for link in article_links:
            # Assurez-vous que le lien est absolu
            yield response.follow(link, self.parse_article)

        # Logique pour suivre la pagination (si nécessaire)
        # next_page = response.css('a.next-page::attr(href)').get()
        # if next_page is not None:
        #     yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        # Extraction du contenu de l'article
        title = response.css('h1.page-title::text').get()
        # Extraction des paragraphes de contenu
        content_paragraphs = response.css('div.article-content p::text').getall()
        content = " ".join(content_paragraphs).strip()
        
        # Extraction de la date de publication
        # Le sélecteur exact dépend du site, ici une simulation
        date_str = response.css('span.post-date::text').get()
        publish_date = self._normalize_date(date_str)
        
        # Le contenu brut à passer au pipeline ETL
        raw_data_item = {
            "source_type": self.source_type,
            "url": response.url,
            "weight": self.source_weight,
            "content": f"{title}. {content}",
            "publish_date": publish_date
        }
        
        # Passer l'élément au pipeline ETL pour la transformation et le chargement
        yield raw_data_item

    def _normalize_date(self, date_str):
        # Fonction simplifiée pour normaliser la date (à adapter si le format Hespress est complexe)
        # Pour l'instant, nous retournons la date du jour
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Note: Le pipeline Scrapy doit être configuré pour recevoir ces items
# et les passer à la classe Transformer.
