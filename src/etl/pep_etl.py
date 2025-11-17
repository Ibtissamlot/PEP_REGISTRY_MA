import uuid
import json
from datetime import datetime, timezone
from src.config import Config
from src.db_connector import DBConnector
from src.etl.exporter import Exporter
from src.etl.loader import Loader
from src.etl.transformer import Transformer

class PEPRegistryETL:
    """
    Classe principale pour gérer le pipeline ETL du registre PPE.
    Assure la modularité en chargeant la configuration spécifique au pays.
    """
    
    def __init__(self, country_code: str = "MA"):
        self.config = Config(country_code)
        self.country_code = self.config.country_code
        print(f"Initialisation du pipeline ETL pour le pays: {self.config.get('country_name')}")

    def run_pipeline(self):
        """Orchestre les étapes E, T et L du pipeline."""
        print("--- ÉTAPE 1: EXTRACTION (E) ---")
        raw_data = self._extract_data()
        
        print("--- ÉTAPE 2: TRANSFORMATION (T) ---")
        self.transformer = Transformer(self.config.data)
        processed_records = self.transformer.process_raw_data(raw_data)
        
        print("--- ÉTAPE 3: CHARGEMENT (L) ---")
        self.loader = Loader(self.country_code)
        self.loader.load_records(processed_records)
        
        print("--- ÉTAPE 4: EXPORT (X) ---")
        exporter = Exporter(output_dir=f"pep_registry/exports/{self.country_code}")
        exporter.generate_json_export()
        exporter.generate_csv_export()
        
        print(f"Pipeline ETL pour {self.country_code} terminé.")

    def _extract_data(self):
        """
        Implémentation de l'extraction.
        Pour la simulation, nous allons simplement retourner une liste de sources.
        En production, cette méthode appellerait les crawlers Scrapy.
        """
        raw_sources = []
        
        # --- LOGIQUE D'EXTRACTION RÉELLE ---
        # En production, cette méthode appellerait les crawlers Scrapy.
        # Pour l'instant, nous allons simuler le résultat d'un crawler Scrapy
        # en utilisant des données plus réalistes basées sur les sources.
        
        # NOTE: Pour une implémentation réelle, vous devriez créer un projet Scrapy
        # et appeler les crawlers ici.
        
        # Appel du Scrapy Crawler
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        from src.etl.spiders.hespress_spider import HespressSpider
        
        # Configuration Scrapy (à adapter si nécessaire)
        settings = get_project_settings()
        settings.set('LOG_LEVEL', 'INFO')
        # Désactiver la configuration par défaut du pipeline qui cause une erreur
        # settings.set('ITEM_PIPELINES', {
        #     'src.etl.pipelines.RawDataPipeline': 300,
        # })
        
        process = CrawlerProcess(settings)
        
        # Liste pour stocker les résultats du crawler
        raw_data_list = []
        
        # Définir un pipeline temporaire pour capturer les données
        class RawDataPipeline:
            def process_item(self, item, spider):
                raw_data_list.append(dict(item))
                return item
        
        # Ajouter le pipeline temporaire
        process.settings.set('ITEM_PIPELINES', {
            __name__ + '.RawDataPipeline': 300,
        })
        
        # Lancer le crawler
        process.crawl(HespressSpider)
        process.start()  # Le processus est bloquant jusqu'à ce que tous les crawlers soient terminés
        
        print(f"Extraction réelle via Scrapy terminée. {len(raw_data_list)} éléments capturés.")
        return raw_data_list
        




if __name__ == '__main__':
    # Exemple d'exécution du pipeline pour le Maroc
    etl = PEPRegistryETL(country_code="MA")
    etl.run_pipeline()
