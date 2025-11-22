import scrapy

class LEconomisteRSSSpider(scrapy.Spider):
    custom_settings = {
        'DOWNLOAD_DELAY': 5,  # Ajouter un délai de 5 secondes entre les requêtes
        'HTTPERROR_ALLOWED_CODES': [403], # Permettre de traiter les réponses 403
    }
    name = 'leconomiste_rss'
    allowed_domains = ['www.leconomiste.com']
    # Utilisation directe du flux RSS pour la découverte des articles
    start_urls = ['https://www.leconomiste.com/rss-leconomiste/4579']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, dont_filter=True)

    def parse(self, response):
        # Vérifier si la réponse est un 403
        if response.status == 403:
            self.logger.error(f"Requête bloquée par le serveur (403) pour l'URL: {response.url}. Le scraping ne peut pas continuer.")
            return # Arrêter le scraping si le flux RSS est bloqué

        # Le flux RSS est en XML, nous utilisons les sélecteurs XML/XPath
        # Chaque article est dans une balise <item>
        for item in response.xpath('//item'):
            # Extraction du lien de l'article à partir de la balise <link>
            link = item.xpath('./link/text()').get()
            
            if link:
                # Suivre le lien pour scraper le contenu complet de l'article
                yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        # Extraction du contenu de l'article à partir de la page HTML
        title = response.css('h1::text').get()
        
        # Sélecteurs génériques pour le contenu de l'article
        content_paragraphs = response.css('.article-content p::text, .post-content p::text, .entry-content p::text, div[itemprop="articleBody"] p::text').getall()
        content = ' '.join(content_paragraphs).strip()
        
        # Extraction de la date (si disponible)
        date_published = response.css('.post-date::text, .article-date::text').get()
        
        # Vérification minimale pour s'assurer que l'article est pertinent
        if title and content:
            yield {
                'url': response.url,
                'title': title.strip(),
                'content': content,
                'source': 'L\'Economiste',
                'date_published': date_published.strip() if date_published else None,
                'date_scraped': scrapy.Field(), # Sera rempli par le pipeline
            }
