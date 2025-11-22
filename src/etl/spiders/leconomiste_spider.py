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
        # Sélecteur pour les liens d'articles sur la page de liste
        # Le sélecteur le plus fiable semble être 'a[href]' dans le corps de la page, 
        # mais nous allons cibler les liens qui ne sont pas des catégories ou des éditoriaux.
        # Le pattern d'URL des articles est généralement /annee/mois/jour/titre/
        article_links = response.css('a[href*="/2025/"]::attr(href), a[href*="/2024/"]::attr(href), a[href*="/2023/"]::attr(href)').getall()
        
        # Ajout des liens de la page d'accueil qui ne suivent pas le pattern de date
        article_links.extend(response.css('a[href*="de-bonnes-sources-"]::attr(href), a[href*="appel-doffres-onicl-"]::attr(href)').getall())
        
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
