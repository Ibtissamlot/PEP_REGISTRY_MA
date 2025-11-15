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
        
        # Données de test plus réalistes pour le Maroc
        real_raw_data = [
            {
                "source_type": "official",
                "url": "https://www.oc.gov.ma/actualites/nomination-ministre-finances",
                "weight": 0.6,
                "content": "Le Bulletin Officiel confirme la nomination de Monsieur Mohamed Benchaaboun au poste de Ministre des Finances. La nomination a été faite par décret royal.",
                "publish_date": "2024-10-20"
            },
            {
                "source_type": "media",
                "url": "https://fr.hespress.com/politique/le-nouveau-wali-de-rabat-est-mme-fatima-zohra",
                "weight": 0.2,
                "content": "Selon Hespress, le nouveau Wali de la région de Rabat-Salé-Kénitra est Madame Fatima Zohra El Alaoui. Elle a été nommée par décret royal en date du 20 octobre 2024.",
                "publish_date": "2024-10-21"
            },
            {
                "source_type": "media",
                "url": "https://telquel.ma/actualite/demission-du-dg-de-l-ammc",
                "weight": 0.2,
                "content": "TelQuel rapporte la démission de Monsieur Hassan Bouknadel de son poste de Directeur Général de l'AMMC. La démission prend effet immédiatement.",
                "publish_date": "2024-10-25"
            },
            {
                "source_type": "official",
                "url": "https://www.courdescomptes.ma/rapport-2024",
                "weight": 0.5,
                "content": "La Cour des Comptes a publié son rapport annuel 2024, mentionnant des irrégularités dans la gestion de l'ancien Ministre de l'Équipement, M. Abdelkader Amara.",
                "publish_date": "2024-11-01"
            }
        ]
        
        print(f"Extraction simulée de {len(real_raw_data)} sources plus réalistes.")
        return real_raw_data
        
    def _extract_data(self):
        """
        Implémentation de l'extraction.
        Pour la simulation, nous allons simplement retourner une liste de sources.
        En production, cette méthode appellerait les crawlers Scrapy.
        """
        raw_sources = []
        
        # --- LOGIQUE D'EXTRACTION RÉELLE (SIMULÉE AVEC DES DONNÉES PLUS RÉALISTES) ---
        # En production, cette méthode appellerait les crawlers Scrapy.
        # Pour l'instant, nous allons simuler le résultat d'un crawler Scrapy
        # en utilisant des données plus réalistes basées sur les sources.
        
        # NOTE: Pour une implémentation réelle, vous devriez créer un projet Scrapy
        # et appeler les crawlers ici.
        
        # Données de test plus réalistes pour le Maroc
        real_raw_data = [
            {
                "source_type": "official",
                "url": "https://www.oc.gov.ma/actualites/nomination-ministre-finances",
                "weight": 0.6,
                "content": "Le Bulletin Officiel confirme la nomination de Monsieur Mohamed Benchaaboun au poste de Ministre des Finances. La nomination a été faite par décret royal.",
                "publish_date": "2024-10-20"
            },
            {
                "source_type": "media",
                "url": "https://fr.hespress.com/politique/le-nouveau-wali-de-rabat-est-mme-fatima-zohra",
                "weight": 0.2,
                "content": "Selon Hespress, le nouveau Wali de la région de Rabat-Salé-Kénitra est Madame Fatima Zohra El Alaoui. Elle a été nommée par décret royal en date du 20 octobre 2024.",
                "publish_date": "2024-10-21"
            },
            {
                "source_type": "media",
                "url": "https://telquel.ma/actualite/demission-du-dg-de-l-ammc",
                "weight": 0.2,
                "content": "TelQuel rapporte la démission de Monsieur Hassan Bouknadel de son poste de Directeur Général de l'AMMC. La démission prend effet immédiatement.",
                "publish_date": "2024-10-25"
            },
            {
                "source_type": "official",
                "url": "https://www.courdescomptes.ma/rapport-2024",
                "weight": 0.5,
                "content": "La Cour des Comptes a publié son rapport annuel 2024, mentionnant des irrégularités dans la gestion de l'ancien Ministre de l'Équipement, M. Abdelkader Amara.",
                "publish_date": "2024-11-01"
            }
        ]
        
        print(f"Extraction simulée de {len(real_raw_data)} sources plus réalistes.")
        return real_raw_data



if __name__ == '__main__':
    # Exemple d'exécution du pipeline pour le Maroc
    etl = PEPRegistryETL(country_code="MA")
    etl.run_pipeline()
