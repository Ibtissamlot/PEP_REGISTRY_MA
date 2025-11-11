import json
from pathlib import Path

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

# Configuration de la base de données (pour la simulation, nous utilisons les paramètres par défaut)
DB_CONFIG = {
    "database": "pep_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}
