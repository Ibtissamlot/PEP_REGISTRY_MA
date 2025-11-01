from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any, Optional
from src.db_connector import DBConnector

app = FastAPI(
    title="PEP Registry API - Morocco",
    description="API REST pour l'accès au registre des Personnes Politiquement Exposées (PPE) marocaines, avec historique et auditabilité.",
    version="1.0.0"
)

# Fonction utilitaire pour récupérer les données d'un PEP
def fetch_pep_details(pep_id: str, fetch_history: bool = False) -> Optional[Dict[str, Any]]:
    """Récupère les détails du PEP à partir de la base de données."""
    try:
        with DBConnector() as db:
            # Récupérer la version actuelle
            query_current = """
            SELECT pv.data_jsonb
            FROM pep_master pm
            JOIN pep_version pv ON pm.current_version_id = pv.version_id
            WHERE pm.id = %s;
            """
            current_data = db.execute(query_current, (pep_id,), fetch=True)
            
            if not current_data:
                return None
            
            result = current_data[0]['data_jsonb']
            
            if fetch_history:
                # Récupérer l'historique des versions
                query_history = """
                SELECT version_id, confidence_score, status, last_updated
                FROM pep_version
                WHERE pep_id = %s
                ORDER BY last_updated DESC;
                """
                result['version_history'] = db.execute(query_history, (pep_id,), fetch=True)
                
                # Récupérer l'audit log
                query_audit = """
                SELECT timestamp, actor, source, reason
                FROM audit_log
                WHERE pep_id = %s
                ORDER BY timestamp DESC;
                """
                result['audit_log'] = db.execute(query_audit, (pep_id,), fetch=True)
                
            return result
            
    except Exception as e:
        print(f"Erreur de base de données: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur lors de la récupération des données.")

@app.get("/peps", response_model=List[Dict[str, Any]], summary="Liste et filtre les enregistrements PPE actifs")
async def list_peps(
    country_code: str = Query("MA", description="Code pays (MA par défaut)"),
    status: str = Query(None, description="Filtrer par statut (active, former, under_review)"),
    min_confidence: float = Query(None, description="Score de confiance minimum (0.0 à 1.0)"),
    limit: int = Query(100, description="Nombre maximum de résultats"),
    offset: int = Query(0, description="Décalage pour la pagination")
):
    """
    Récupère une liste paginée des enregistrements PPE.
    """
    try:
        with DBConnector() as db:
            base_query = """
            SELECT pv.data_jsonb
            FROM pep_master pm
            JOIN pep_version pv ON pm.current_version_id = pv.version_id
            WHERE pm.country_code = %s
            """
            params = [country_code]
            
            if status:
                base_query += " AND pv.status = %s"
                params.append(status)
            
            if min_confidence is not None:
                base_query += " AND pv.confidence_score >= %s"
                params.append(min_confidence)
                
            base_query += " LIMIT %s OFFSET %s;"
            params.extend([limit, offset])
            
            results = db.execute(base_query, tuple(params), fetch=True)
            
            return [res['data_jsonb'] for res in results]
            
    except Exception as e:
        print(f"Erreur de base de données: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")

@app.get("/peps/{pep_id}", summary="Récupère les détails complets d'un PPE")
async def get_pep_details(pep_id: str):
    """
    Récupère la version actuelle d'un enregistrement PPE par son ID.
    """
    pep_data = fetch_pep_details(pep_id)
    if pep_data is None:
        raise HTTPException(status_code=404, detail="PPE non trouvé.")
    return pep_data

@app.get("/peps/{pep_id}/history", summary="Récupère les détails, l'historique des versions et l'audit log d'un PPE")
async def get_pep_history(pep_id: str):
    """
    Récupère la version actuelle, l'historique des versions et le journal d'audit pour un enregistrement PPE.
    """
    pep_data = fetch_pep_details(pep_id, fetch_history=True)
    if pep_data is None:
        raise HTTPException(status_code=404, detail="PPE non trouvé.")
    return pep_data

@app.get("/metrics/last_updated", summary="Retourne la date et l'heure de la dernière mise à jour du registre")
async def get_last_updated():
    """
    Retourne le timestamp de la dernière exécution réussie du pipeline ETL.
    """
    try:
        with DBConnector() as db:
            query = """
            SELECT last_updated
            FROM pep_version
            ORDER BY last_updated DESC
            LIMIT 1;
            """
            result = db.execute(query, fetch=True)
            if result:
                return {"last_updated": result[0]['last_updated'].isoformat()}
            return {"last_updated": "N/A"}
    except Exception as e:
        print(f"Erreur de base de données: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")
