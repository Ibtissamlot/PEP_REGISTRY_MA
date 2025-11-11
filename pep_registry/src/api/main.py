@router.get("/peps", response_model=List[Pep])
def list_peps(country_code: str, limit: int = 5000, offset: int = 0):
    try:
        # LIGNE À MODIFIER : Utilisez la CLASSE pour créer une nouvelle instance dans le bloc 'with'
        with DBConnector() as db: 
            query = "SELECT * FROM peps WHERE country_code = %s LIMIT %s OFFSET %s"
            peps = db.execute(query, (country_code, limit, offset), fetch=True)
            return peps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {e}")
