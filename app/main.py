# app/main.py
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import books, authors

# Les infos de base de l'API
app = FastAPI(
    title="La Bibliothèque",
    description="API REST dédiée à la gestion des livres, des auteurs, des emprunts et un système de recherche avancé",
    version="1.0.0",
)

# On importe le fichier des books et des authors
app.include_router(books.router)
app.include_router(authors.router)

# Création de la base de données et lancement de la fonction (create_db_and_tables) à l'exécution du script 
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# On définit un message de bienvenue pour la route root
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de La Bibliothèque"}
