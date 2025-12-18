# API de Gestion de "La Bibliothèque"

API REST développée avec le framework FastAPI pour gérer les livres, les auteurs et les emprunts d'une bibliothèque.

## Installation

```bash
# Créer l'environnement virtuel
python -m venv mon_env

# Activer l'environnement
# Windows:
mon_env\Scripts\activate
# Linux/Mac:
source mon_env/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

##  Lancement

```bash
uvicorn app.main:app --reload
```

L'API sera accessible sur `http://localhost:8000`  
La Documentation Swagger sera accessible sur : `http://localhost:8000/docs`

## Endpoints principaux

### Livres
- `GET /books/` - Liste paginée des livres
- `POST /books/` - Créer un livre
- `GET /books/{book_id}` - Détails d'un livre
- `PATCH /books/{book_id}` - Modifier un livre
- `DELETE /books/{book_id}` - Supprimer un livre
- `GET /books/search/` - Recherche avancée

### Auteurs
- `GET /authors/` - Liste paginée des auteurs
- `POST /authors/` - Créer un auteur
- `GET /authors/{author_id}` - Détails d'un auteur
- `PATCH /authors/{author_id}` - Modifier un auteur
- `DELETE /authors/{author_id}` - Supprimer un auteur
- `GET /authors/search/` - Rechercher des auteurs

### Emprunts
- `POST /loans/` - Créer un emprunt
- `POST /loans/{loan_id}/return` - Retourner un livre (clôturer l'emprunt)
- `POST /loans/{loan_id}/renew` - Renouveler/continuer un emprunt (Cela ajoute 14 jours et 1 fois maximum)
- `GET /loans/` - Lister les emprunts (avec les statuts actif, en retard ou afficher l'historique)

## Technologies

- **FastAPI** - Framework web moderne et rapide
- **SQLModel** - ORM basé sur SQLAlchemy et Pydantic
- **SQLite** - Base de données légère
- **Pydantic** - Validation des données

## Structure

```
├── app/
│   ├── main.py         # Point d'entrée de l'API
│   └── database.db     # Base de données SQLite
├── mon_env/            # Environnement virtuel
└── sujet_bibli.md      # Spécifications détaillées
```