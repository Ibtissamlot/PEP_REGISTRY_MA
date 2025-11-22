import scrapy

class Le360Spider(scrapy.Spider):
    name = 'le360'
    allowed_domains = ['fr.le360.ma']
    start_urls = [
        'https://fr.le360.ma/politique/',
        'https://fr.le360.ma/economie/'
    ]

    def parse(self, response):
        # Sélecteur pour les liens d'articles sur la page de liste (Politique/Economie)
        # Basé sur l'inspection de la page fr.le360.ma/politique/
        # Les liens sont dans des balises <a> qui sont les enfants directs de <div> sans classe
        # ou dans des balises <a> avec un attribut id="card-list--headline-link"
        article_links = response.css('article a::attr(href), #card-list--headline-link::attr(href)').getall()
        
        all_links = set(article_links)

        for link in all_links:
            # Assurez-vous que le lien est complet
            yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        # Extraction du contenu de l'article
        title = response.css('h1::text').get()
        # Le contenu est dans des balises <p> à l'intérieur d'un <div> avec la classe "article-content"
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
