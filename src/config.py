import os
import json
from pathlib import Path
from urllib.parse import urlparse

class Config:
    """Gère le chargement de la configuration spécifique à un pays."""
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_DIR = BASE_DIR / "config"
    
    def __init__(self, country_code: str = "MA"):
        self.country_code = country_code.upper()
        self.config_file = self.CONFIG_DIR / f"{self.country_code.lower()}.json"
        self.data = self._load_config()

    def _load_config(self):
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found for country code {self.country_code}: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)

# --- CORRECTION APPLIQUÉE ---
# Lire l'URL de la base de données à partir de la variable d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Parser l'URL pour extraire les composants de connexion
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        "database": result.path[1:], # Supprime le '/' au début
        "user": result.username,
        "password": result.password,
        "host": result.hostname,
        "port": result.port
    }
else:
    # Utiliser une configuration locale par défaut si DATABASE_URL n'est pas définie
    print("WARNING: DATABASE_URL environment variable not set. Using local default.")
    DB_CONFIG = {
        "database": "pep_db",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432
    }
