import scrapy

class LEconomisteSpider(scrapy.Spider):
    name = 'leconomiste'
    allowed_domains = ['www.leconomiste.com']
    login_url = 'https://www.leconomiste.com/connexion'
    start_urls = [
        'https://www.leconomiste.com/',
        'https://www.leconomiste.com/categorie/economie',
        'https://www.leconomiste.com/categorie/politique'
    ]

    def start_requests(self):
        # Récupérer les identifiants depuis les settings (variables d'environnement)
        username = self.settings.get('LECONOMISTE_USERNAME')
        password = self.settings.get('LECONOMISTE_PASSWORD')

        if username and password:
            self.logger.info(f"Identifiants trouvés. Démarrage de la séquence d'authentification pour l'utilisateur: {username[:3]}***.")
            # 1. Requête pour la page de connexion pour obtenir le jeton CSRF (si nécessaire)
            yield scrapy.Request(
                url=self.login_url,
                callback=self.parse_login_page
            )
        else:
            self.logger.warning("Identifiants LECONOMISTE_USERNAME ou LECONOMISTE_PASSWORD non trouvés. Démarrage du scraping sans authentification.")
            # Si pas d'identifiants, continuer sans authentification (pour les articles gratuits)
            for url in self.start_urls:
                yield scrapy.Request(url, self.parse)

    def parse_login_page(self, response):
        # Tenter de trouver le jeton CSRF (souvent un champ caché)
        csrf_token = response.css('input[name="_token"]::attr(value)').get()
        
        # Récupérer les identifiants depuis les settings (variables d'environnement)
        username = self.settings.get('LECONOMISTE_USERNAME')
        password = self.settings.get('LECONOMISTE_PASSWORD')

        # 2. Requête POST pour l'authentification
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'username': username,
                'password': password,
                # Ajouter le jeton CSRF si trouvé
                '_token': csrf_token if csrf_token else '',
            },
            callback=self.after_login,
            dont_filter=True
        )

    def after_login(self, response):
        # Vérifier si la connexion a réussi
        if "Mon Compte" in response.text or "Déconnexion" in response.text:
            self.logger.info("Connexion à L'Economiste réussie. Démarrage du scraping.")
        else:
            self.logger.error("Échec de la connexion à L'Economiste. Le scraping continuera avec les articles gratuits.")

        # Démarrer le scraping des URLs
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        # Sélecteur pour les liens d'articles sur la page de liste
        # Basé sur l'inspection de la page d'accueil et des catégories
        # Les liens d'articles sont souvent dans des balises <a> qui contiennent un titre ou une image
        # Sélecteur pour les liens d'articles sur la page de liste
        # Le sélecteur le plus fiable semble être 'a[href]' dans le corps de la page, 
        # mais nous allons cibler les liens qui ne sont pas des catégories ou des éditoriaux.
        # Sélecteur agressif pour les liens d'articles: tout lien qui ressemble à un article (contient une date ou un titre long)
        # Nous allons utiliser un sélecteur plus large pour capturer plus de liens.
        article_links = response.css('a[href*="/2025/"]::attr(href), a[href*="/2024/"]::attr(href), a[href*="/2023/"]::attr(href), a[href*="-"]::attr(href)').getall()
        
        # Filtrer les liens qui sont des catégories ou des éditoriaux
        article_links = [link for link in article_links if not any(keyword in link for keyword in ['/categorie/', '/editorial/', '/rss-leconomiste/'])]
        
        # S'assurer que les liens sont uniques
        article_links = list(set(article_links))
        
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
        # Ajout de sélecteurs plus génériques pour le contenu de l'article
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
