import scrapy

class Le360Spider(scrapy.Spider):
    name = 'le360'
    allowed_domains = ['fr.le360.ma']
    start_urls = [
        'https://fr.le360.ma/politique/',
        'https://fr.le360.ma/economie/'
    ]

    def parse(self, response):
        # Sélecteur pour les liens d'articles dans la section principale
        # Basé sur l'inspection de la page fr.le360.ma/politique/
        article_links = response.css('h2 a::attr(href), h3 a::attr(href), .article-list-item a::attr(href)').getall()
        
        # Sélecteur pour les liens dans la colonne latérale "Fil d'actualité"
        sidebar_links = response.css('.sidebar-block a::attr(href)').getall()
        
        all_links = set(article_links + sidebar_links)

        for link in all_links:
            # Assurez-vous que le lien est complet
            yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        # Extraction du contenu de l'article
        title = response.css('h1::text').get()
        content_paragraphs = response.css('.article-content p::text').getall()
        content = ' '.join(content_paragraphs).strip()
        
        # Vérification minimale pour s'assurer que l'article est pertinent
        if title and content:
            yield {
                'url': response.url,
                'title': title.strip(),
                'content': content,
                'source': 'Le360',
                'date_scraped': scrapy.Field(), # Sera rempli par le pipeline
            }
