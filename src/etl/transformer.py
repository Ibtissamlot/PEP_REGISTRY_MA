import spacy
from fuzzywuzzy import fuzz
from datetime import datetime, timezone
from typing import List, Dict, Any
from src.db_connector import DBConnector
import uuid

# Charger le modèle de PNL français
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    print("Modèle fr_core_news_sm non trouvé. Veuillez l'installer avec 'python3 -m spacy download fr_core_news_sm'")
    nlp = None

class Transformer:
    """
    Gère les étapes de Transformation (T) du pipeline ETL:
    Normalisation, Extraction d'Entités Nommées (PNL), Déduplication et Scoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.country_code = config.get('country_code', 'MA')
        self.source_weights = self._get_source_weights()

    def _get_source_weights(self) -> Dict[str, float]:
        """Compile les poids des sources pour le calcul du score de confiance."""
        weights = {}
        for type_key, sources in self.config.get('sources', {}).items():
            for source in sources:
                weights[source['url']] = source['weight']
        return weights

    def normalize_text(self, text: str) -> str:
        """Nettoie et normalise le texte pour la déduplication et la recherche."""
        if not text:
            return ""
        # Convertir en minuscules, retirer les accents, etc. (simplifié pour la simulation)
        return text.lower().strip()

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Utilise le PNL pour l'Extraction d'Entités Nommées (EEN)."""
        if not nlp:
            return []
        
        doc = nlp(text)
        entities = []
        
        # Simuler l'extraction de Personnes (PER) et d'Organisations (ORG) pertinentes
        for ent in doc.ents:
            if ent.label_ in ["PER", "ORG"]:
                entities.append({"text": ent.text, "label": ent.label_})
        
        # Logique d'extraction de titres de poste (simplifiée)
        for keyword in self.config.get('keywords', []):
            if keyword in self.normalize_text(text):
                entities.append({"text": keyword, "label": "JOB_TITLE"})
                
        return entities

    def calculate_confidence_score(self, source_urls: List[str]) -> float:
        """Calcule le score de confiance basé sur la pondération des sources."""
        score = 0.0
        unique_urls = set(source_urls)
        
        for url in unique_urls:
            score += self.source_weights.get(url, 0.0) # 0.0 si la source n'est pas répertoriée
            
        return min(score, 1.0) # Plafonner le score à 1.0

    def find_potential_pep(self, full_name: str) -> Dict[str, Any]:
        """
        Recherche dans la base de données un PEP existant par déduplication (fuzzy matching).
        Retourne l'enregistrement maître si trouvé, sinon None.
        """
        normalized_name = self.normalize_text(full_name)
        
        # 1. Recherche exacte (simulée)
        with DBConnector() as db:
            # Récupérer tous les noms de PEP actifs pour le pays
            query = """
            SELECT pm.id, pm.master_name, pv.data_jsonb->>'full_name' AS current_full_name
            FROM pep_master pm
            JOIN pep_version pv ON pm.current_version_id = pv.version_id
            WHERE pm.country_code = %s;
            """
            existing_peps = db.execute(query, (self.country_code,), fetch=True)
            
            best_match = None
            highest_score = 85 # Seuil de similarité pour le fuzzy matching
            
            for pep in existing_peps:
                # 2. Fuzzy Matching (basé sur le nom complet actuel)
                score = fuzz.token_sort_ratio(normalized_name, self.normalize_text(pep['current_full_name']))
                
                if score > highest_score:
                    highest_score = score
                    best_match = pep
            
            if best_match:
                print(f"Déduplication: Correspondance trouvée pour '{full_name}' avec '{best_match['current_full_name']}' (Score: {highest_score}).")
                return best_match
            
            return None

    def process_raw_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processus principal de transformation:
        1. Insertion des sources dans la DB.
        2. Extraction des entités.
        3. Création des enregistrements PPE potentiels.
        4. Déduplication.
        """
        
        # Étape 1: Insertion des sources dans la DB (pour obtenir les source_id)
        source_ids = {}
        with DBConnector() as db:
            for i, source in enumerate(raw_data):
                query = """
                INSERT INTO source_document (url, title, snippet, publish_date, raw_data_path)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET title = EXCLUDED.title
                RETURNING source_id;
                """
                title = f"Source {i+1} - {source['source_type']}"
                snippet = source['content'][:50] + "..."
                date_str = source['publish_date']
                
                # Simuler le chemin vers le Data Lake
                raw_data_path = f"/data/{self.country_code}/{source['source_type']}_{i}.html"
                
                source_id = db.execute(query, (source['url'], title, snippet, date_str, raw_data_path), fetch=True)[0]['source_id']
                source_ids[source['url']] = source_id
        
        # Étape 2: Extraction des entités et création des enregistrements PPE potentiels
        potential_peps = {} # {full_name: {sources: [], positions: []...}}
        
        for source in raw_data:
            entities = self.extract_entities(source['content'])
            
            # Logique simplifiée: si une PERSONNE et un TITRE DE POSTE sont trouvés ensemble
            person_names = [e['text'] for e in entities if e['label'] == 'PER']
            job_titles = [e['text'] for e in entities if e['label'] == 'JOB_TITLE']
            
            for name in person_names:
                if name not in potential_peps:
                    potential_peps[name] = {"sources": [], "positions": []}
                
                # Ajouter la source
                source_url = source['url']
                source_id = source_ids[source_url]
                
                potential_peps[name]['sources'].append(source_url)
                
                # Ajouter la position (si un titre de poste est trouvé)
                if job_titles:
                    potential_peps[name]['positions'].append({
                        "title": job_titles[0],
                        "institution": "Institution Déduite (Simulée)",
                        "source_id": source_id
                    })
        
        # Étape 3: Vérification et Finalisation des enregistrements
        final_records = []
        for full_name, data in potential_peps.items():
            
            # Calcul du score de confiance
            confidence_score = self.calculate_confidence_score(data['sources'])
            
            # Appliquer la règle de vérification (score >= 0.6 pour auto-création)
            if confidence_score < 0.6:
                status = "under_review"
            else:
                status = "active"
            
            # Déduplication
            master_record = self.find_potential_pep(full_name)
            if master_record:
                pep_id = master_record['id']
            else:
                pep_id = str(uuid.uuid4())
            
            now = datetime.now(timezone.utc).isoformat()
            
            # Création du corps JSONB (simplifié)
            pep_record = {
                "id": pep_id,
                "full_name": full_name,
                "aliases": [self.normalize_text(full_name)],
                "gender": None,
                "date_of_birth": None,
                "nationality": [self.country_code],
                "relationship_type": ["DomesticPEP"], # Simplifié
                "current_positions": data['positions'],
                "past_positions": [],
                "family_members": [],
                "associated_entities": [],
                "sanctions_match": [],
                "confidence_score": confidence_score,
                "source_documents": [
                    {"source_id": source_ids[url], "snippet": "Snippet simulé...", "publish_date": now[:10]}
                    for url in set(data['sources'])
                ],
                "first_seen": now,
                "last_updated": now,
                "status": status,
                "notes": f"Enregistrement créé par le pipeline ETL. Score: {confidence_score}"
            }
            
            final_records.append({
                "pep_id": pep_id,
                "record": pep_record,
                "confidence_score": confidence_score,
                "status": status
            })
            
        return final_records

# Mise à jour de PEPRegistryETL pour utiliser le Transformer
from src.etl.transformer import Transformer

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
        self._load_data(processed_records)
        
        print(f"Pipeline ETL pour {self.country_code} terminé.")

    # ... (méthodes _extract_data et _load_data existantes) ...
