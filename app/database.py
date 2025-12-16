# app/database.py
import os
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv

# On définit les paramètres de la base de données (J'importe le nom du fichier depuis le .env)
load_dotenv()
sqlite_file_name = os.getenv('sqlite_file_name')
engine = create_engine(
    f"sqlite:///{sqlite_file_name}",
    connect_args={"check_same_thread": False},
)

# Création de la base de données et lancement de la fonction (create_db_and_tables) à l'exécution du script 
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)