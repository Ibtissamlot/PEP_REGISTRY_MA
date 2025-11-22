import scrapy

class LeMatinRSSSpider(scrapy.Spider):
    name = 'lematin_rss'
    allowed_domains = ['lematin.ma']
    # Utilisation directe du flux RSS pour la découverte des articles
    start_urls = ['https://lematin.ma/rss']

    def parse(self, response):
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
        
        # Sélecteurs génériques pour le contenu de l'article sur lematin.ma
        # Basé sur l'inspection rapide de la structure des articles du Matin
        content_paragraphs = response.css('.article-body p::text, .article-content p::text').getall()
        content = ' '.join(content_paragraphs).strip()
        
        # Extraction de la date (si disponible)
        date_published = response.css('.date-published::text, .article-date::text').get()
        
        # Vérification minimale pour s'assurer que l'article est pertinent
        if title and content:
            yield {
                'url': response.url,
                'title': title.strip(),
                'content': content,
                'source': 'Le Matin',
                'date_published': date_published.strip() if date_published else None,
                'date_scraped': scrapy.Field(), # Sera rempli par le pipeline
            }
