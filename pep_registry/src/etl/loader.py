import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from src.db_connector import DBConnector

class Loader:
    """
    Gère le chargement (L) des enregistrements PPE dans la base de données,
    en appliquant la logique de versioning, d'audit log et de gestion des statuts.
    """
    
    def __init__(self, country_code: str):
        self.country_code = country_code

    def load_records(self, processed_records: List[Dict[str, Any]]):
        """Charge une liste d'enregistrements PPE transformés."""
        if not processed_records:
            print("Aucun enregistrement à charger.")
            return

        with DBConnector() as db:
            for record_data in processed_records:
                self._process_single_record(db, record_data)

    def _process_single_record(self, db: DBConnector, record_data: Dict[str, Any]):
        """Traite et charge un seul enregistrement, gérant la mise à jour ou la création."""
        
        pep_id = uuid.UUID(record_data['pep_id'])
        record = record_data['record']
        confidence_score = record_data['confidence_score']
        status = record_data['status']
        
        # 1. Vérifier si le PEP existe dans pep_master
        master_record = db.execute("SELECT id, current_version_id FROM pep_master WHERE id = %s", (str(pep_id),), fetch=True)
        
        is_new_pep = not master_record
        version_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        # 2. Logique de mise à jour/création dans pep_master
        if is_new_pep:
            # Insertion dans pep_master (avec version_id temporaire)
            query_master = """
            INSERT INTO pep_master (id, country_code, master_name, current_version_id)
            VALUES (%s, %s, %s, %s);
            """
            db.execute(query_master, (str(pep_id), self.country_code, record['full_name'], str(version_id)))
            audit_reason = "Nouveau PEP créé par le pipeline ETL."
        else:
            # Récupérer la version précédente pour comparaison
            prev_version_id = master_record[0]['current_version_id']
            prev_version = db.execute("SELECT data_jsonb FROM pep_version WHERE version_id = %s", (str(prev_version_id),), fetch=True)
            
            # Comparaison: Si le JSONB de la nouvelle version est différent de l'ancienne
            # (En production, une comparaison structurelle plus fine serait nécessaire)
            if json.dumps(record, sort_keys=True) == json.dumps(prev_version[0]['data_jsonb'], sort_keys=True):
                # Aucune modification significative, pas de nouvelle version créée
                print(f"PEP: {record['full_name']} (ID: {pep_id}) inchangé. Saut de la nouvelle version.")
                return 
            
            audit_reason = "Mise à jour de la version du PEP (changement de données)."

        # 3. Insérer une nouvelle version (versioning)
        query_version = """
        INSERT INTO pep_version (version_id, pep_id, data_jsonb, confidence_score, status, first_seen, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        db.execute(query_version, (str(version_id), str(pep_id), json.dumps(record), confidence_score, status, now, now))

        # 4. Mettre à jour current_version_id dans pep_master
        query_master_update = """
        UPDATE pep_master SET current_version_id = %s
        WHERE id = %s;
        """
        db.execute(query_master_update, (str(version_id), str(pep_id)))
        
        # 5. Insérer dans audit_log
        query_audit = """
        INSERT INTO audit_log (pep_id, version_id, actor, source, reason)
        VALUES (%s, %s, %s, %s, %s);
        """
        db.execute(query_audit, (str(pep_id), str(version_id), "ETL_Process", f"Pipeline {self.country_code}", audit_reason))
        
        print(f"Chargement réussi pour PEP: {record['full_name']} (ID: {pep_id}). Nouvelle version: {version_id}. Raison: {audit_reason}")

# Mise à jour de PEPRegistryETL pour utiliser le Loader
from src.etl.loader import Loader

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
        
        print(f"Pipeline ETL pour {self.country_code} terminé.")

    # ... (méthodes _extract_data et _load_data existantes) ...
