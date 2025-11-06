import os
from sqlalchemy import create_engine

# ... autres imports ...

# Récupère l'URL de connexion depuis la variable d'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Lève une erreur si la variable n'est pas définie (sécurité)
    # Ceci est crucial pour éviter l'erreur "localhost"
    raise ValueError("DATABASE_URL environment variable is not set. Cannot connect to database.")

# Crée le moteur de connexion en utilisant l'URL de Supabase
engine = create_engine(DATABASE_URL)

# ... le reste de votre code ...
