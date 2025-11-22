import scrapy

class LEconomisteSpider(scrapy.Spider):
    name = 'leconomiste'
    allowed_domains = ['www.leconomiste.com']
    start_urls = [
        'https://www.leconomiste.com/',
        'https://www.leconomiste.com/categorie/economie',
        'https://www.leconomiste.com/categorie/politique'
    ]

    def parse(self, response):
        # Sélecteur pour les liens d'articles sur la page de liste
        # Basé sur l'inspection de la page d'accueil et des catégories
        # Les liens d'articles sont souvent dans des balises <a> qui contiennent un titre ou une image
        article_links = response.css('h2 a::attr(href), h3 a::attr(href), .post-title a::attr(href), .article-link::attr(href)').getall()
        
        # Le flux RSS semble aussi contenir des liens d'articles
        rss_links = response.css('item link::text').getall()
        
        all_links = set(article_links + rss_links)

        for link in all_links:
            # Assurez-vous que le lien est complet
            yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        # Extraction du contenu de l'article
        title = response.css('h1::text').get()
        
        # Le contenu est souvent dans des balises <p> à l'intérieur d'un conteneur principal
        content_paragraphs = response.css('.article-content p::text, .post-content p::text').getall()
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
