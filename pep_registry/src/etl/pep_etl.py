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
        
        # Simuler l'extraction des sources officielles
        for source in self.config.get('sources', {}).get('official', []):
            raw_sources.append({
                "source_type": "official",
                "url": source["url"],
                "weight": source["weight"],
                "content": f"Le Bulletin Officiel confirme la nomination de Monsieur Ahmed Alami au poste de Ministre des Finances.",
                "publish_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
            })

        # Simuler l'extraction des sources médias
        for source in self.config.get('sources', {}).get('media', []):
            raw_sources.append({
                "source_type": "media",
                "url": source["url"],
                "weight": source["weight"],
                "content": f"Selon {source['name']}, le nouveau Wali de la région de Rabat est Madame Fatima Zohra. Elle a été nommée par décret royal.",
                "publish_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
            })
            
        # Simuler l'extraction des listes de sanctions
        for source in self.config.get('sources', {}).get('sanctions', []):
             raw_sources.append({
                "source_type": "sanction",
                "url": source["url"],
                "weight": source["weight"],
                "content": f"Liste de sanctions simulée de {source['name']}. Le nom de M. Alami n'y figure pas.",
                "publish_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
            })
            
        print(f"Extraction simulée de {len(raw_sources)} sources.")
        return raw_sources



if __name__ == '__main__':
    # Exemple d'exécution du pipeline pour le Maroc
    etl = PEPRegistryETL(country_code="MA")
    etl.run_pipeline()
