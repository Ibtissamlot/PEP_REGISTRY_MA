import sys
import os
import json
import csv
# Ajouter le répertoire parent de 'etl' au chemin Python
# Cela permet de résoudre l'erreur ModuleNotFoundError: No module named 'etl'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialisation du client Supabase
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Liste pour collecter les données brutes
RAW_DATA_LIST = []

def transform_to_pep_master_format(raw_data_list):
    """
    Transforme la liste des données brutes (items Scrapy) en un format
    compatible avec la table 'pep_master' (ou la table de données principales).
    """
    supabase_data = []
    for item in raw_data_list:
        # Vérifier si l'item est un article de L'Economiste
        if item.get('source') == "L'Economiste":
            # Transformation pour la table pep_master
            # Nous insérons les données brutes de l'article.
            
            # Créer l'objet de données pour Supabase
            data_entry = {
                'url': item.get('url'),
                'title': item.get('title'),
                'content': item.get('content'), # Ajout du contenu complet
                'source': item.get('source'),
                'date_published': item.get('date_published'),
                'date_scraped': item.get('date_scraped', datetime.now().isoformat()),
                # Ajoutez ici les autres champs requis par votre table pep_master
            }
            supabase_data.append(data_entry)
        
        # Ajoutez ici la logique de transformation pour d'autres sources si nécessaire
        # elif item.get('source') == 'AutreSource':
        #     ...
            
    return supabase_data

def run_etl_pipeline():
    print("Initialisation du pipeline ETL pour le pays : Maroc")
    
    # ÉTAPE 1 : EXTRACTION (E)
    print("\n--- ÉTAPE 1 : EXTRACTION (E) ---")
    
    # Récupérer les settings Scrapy
    settings = get_project_settings()
    
    # Injecter la liste de données brutes dans les settings pour le pipeline ItemCollector
    settings.set('RAW_DATA_LIST', RAW_DATA_LIST)
    
    # Initialiser le crawler process
    process = CrawlerProcess(settings)
    
    # Importer et ajouter les spiders
    from etl.spiders.leconomiste_spider import LEconomisteSpider
    
    # Ajouter les spiders au processus
    process.crawl(LEconomisteSpider)
    
    # Démarrer le crawling (bloquant)
    process.start()
    
    print(f"Extraction réelle via Scrapy terminée. {len(RAW_DATA_LIST)} éléments capturés.")
    
    # ÉTAPE 2 : TRANSFORMATION (T)
    print("\n--- ÉTAPE 2 : TRANSFORMATION (T) ---")
    
    # Transformer les données brutes en format Supabase pour la table pep_master
    supabase_data = transform_to_pep_master_format(RAW_DATA_LIST)
    
    print(f"Transformation terminée. {len(supabase_data)} enregistrements prêts pour Supabase.")
    
    # ÉTAPE 3 : CHARGEMENT (L)
    print("\n--- ÉTAPE 3 : CHARGEMENT (L) ---")
    
    if supabase_data:
        print(f"{len(supabase_data)} enregistrements à charger.")
        
        # Insertion dans Supabase
        try:
            # Insérer les données dans la table 'pep_master'
            supabase_client.table('pep_version').insert(supabase_data).execute()
            print(f"Chargement (L) terminé. {len(supabase_data)} enregistrements chargés avec succès dans 'pep_master'.")
        except Exception as e:
            print(f"Erreur lors de l'insertion dans Supabase: {e}")
            
        # ÉTAPE 4 : EXPORT (X) - Facultatif, pour la vérification locale
        print("\n--- ÉTAPE 4 : EXPORT (X) ---")
        
        # Générer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"exports/MA/pep_registry_snapshot_{timestamp}.json"
        csv_filename = f"exports/MA/pep_registry_snapshot_{timestamp}.csv"
        
        # Assurez-vous que le répertoire d'exportation existe
        os.makedirs(os.path.dirname(json_filename), exist_ok=True)
        
        # Export JSON
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(supabase_data, f, ensure_ascii=False, indent=4)
        print(f"Export JSON généré: {json_filename}")
        
        # Export CSV
        if supabase_data:
            keys = supabase_data[0].keys()
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(supabase_data)
            print(f"Export CSV généré: {csv_filename}")
        
    else:
        print("Aucun enregistrement à charger.")
        
    print("\nPipeline ETL pour MA terminé.")

if __name__ == '__main__':
    run_etl_pipeline()

