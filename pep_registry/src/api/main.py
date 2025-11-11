from fastapi import FastAPI, HTTPException, APIRouter
from typing import List
from src.db_connector import DBConnector
from src.models import Pep
from src.config import DB_CONFIG # Assurez-vous que DB_CONFIG est bien importé

# Initialisation de l'application FastAPI
app = FastAPI(
    title="PEP Registry API",
    description="API pour le Registre des Personnes Politiquement Exposées (PEP)",
    version="1.0.0",
)

# CRÉATION DU ROUTEUR (DOIT ÊTRE AVANT SON UTILISATION)
router = APIRouter()

# --- Définition des Endpoints ---

@router.get("/peps", response_model=List[Pep])
def list_peps(country_code: str, limit: int = 5000, offset: int = 0):
    """
    Récupère la liste des PEP pour un pays donné.
    """
    try:
        # CORRECTION DBConnector : Utilisation de la CLASSE DBConnector() dans le bloc 'with'
        with DBConnector() as db: 
            query = "SELECT * FROM peps WHERE country_code = %s LIMIT %s OFFSET %s"
            peps = db.execute(query, (country_code, limit, offset), fetch=True)
            return peps
    except Exception as e:
        # Log de l'erreur pour le débogage sur Render
        print(f"Erreur lors de l'exécution de list_peps: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")

# Ajout du routeur à l'application principale (DOIT ÊTRE APRÈS LA DÉFINITION DES ENDPOINTS)
app.include_router(router)

# Endpoint de base pour vérifier que l'API est en ligne
@app.get("/")
def read_root():
    return {"message": "PEP Registry API is running"}

