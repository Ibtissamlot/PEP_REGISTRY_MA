import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from src.db_connector import DBConnector

class Exporter:
    """Gère la génération des exports quotidiens (JSON et CSV)."""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_path = Path(output_dir)
        self.output_path.mkdir(exist_ok=True)

    def _fetch_active_peps(self) -> List[Dict[str, Any]]:
        """Récupère tous les enregistrements PPE actifs (dernière version) de la DB."""
        query = """
        SELECT pv.data_jsonb
        FROM pep_master pm
        JOIN pep_version pv ON pm.current_version_id = pv.version_id
        WHERE pv.status = 'active' OR pv.status = 'under_review';
        """
        with DBConnector() as db:
            results = db.execute(query, fetch=True)
            # data_jsonb est déjà un dictionnaire grâce à RealDictCursor
            return [res['data_jsonb'] for res in results]

    def generate_json_export(self) -> str:
        """Génère l'export JSON complet."""
        records = self._fetch_active_peps()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pep_registry_snapshot_{timestamp}.json"
        filepath = self.output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        
        print(f"Export JSON généré: {filepath}")
        return str(filepath)

    def generate_csv_export(self) -> str:
        """Génère l'export CSV aplati."""
        records = self._fetch_active_peps()
        if not records:
            print("Aucun enregistrement à exporter en CSV.")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pep_registry_snapshot_{timestamp}.csv"
        filepath = self.output_path / filename

        # Définir les champs CSV (aplati)
        fieldnames = [
            "id", "full_name", "nationality", "status", "confidence_score",
            "current_positions_title", "current_positions_institution",
            "sanctions_match_count", "first_seen", "last_updated"
        ]

        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in records:
                # Aplatir les données JSON
                row = {
                    "id": record.get("id"),
                    "full_name": record.get("full_name"),
                    "nationality": ", ".join(record.get("nationality", [])),
                    "status": record.get("status"),
                    "confidence_score": record.get("confidence_score"),
                    "sanctions_match_count": len(record.get("sanctions_match", [])),
                    "first_seen": record.get("first_seen"),
                    "last_updated": record.get("last_updated"),
                }
                
                # Gérer les positions actuelles (prendre la première pour l'export CSV simplifié)
                positions = record.get("current_positions", [])
                if positions:
                    row["current_positions_title"] = positions[0].get("title", "")
                    row["current_positions_institution"] = positions[0].get("institution", "")
                else:
                    row["current_positions_title"] = ""
                    row["current_positions_institution"] = ""
                
                writer.writerow(row)

        print(f"Export CSV généré: {filepath}")
        return str(filepath)

# Mise à jour de PEPRegistryETL pour inclure l'export
from src.etl.exporter import Exporter

class PEPRegistryETL:
    # ... (code existant) ...
    
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

    # ... (méthodes _extract_data et _load_data existantes) ...
