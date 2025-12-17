# app/routers/authors.py
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from app.models import Author, Book
from app.database import engine
from datetime import date, datetime

router = APIRouter(
    prefix="/authors",
    tags=["Auteurs"]
)

# Fonction permettant de formater la date avant de la placer dans la base de données. Nécessaire car sinon nous avons l'erreur 'SQLite Date type only accepts Python date objects as input.'
def formatage_date(v, field_name: str):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        try:
            return date.fromisoformat(v)
        except ValueError:
            raise HTTPException(422, f"Le format de la date est invalide. La date du champ {field_name} doit être au format YYYY-MM-DD")
    raise HTTPException(422, f"Le format de la date est invalide. La date du champ {field_name} doit être au format YYYY-MM-DD")

# Cette route sera destinée à lister tous les auteurs disponibles dans la base de données
@router.get("/")
def read_authors(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
):
    with Session(engine) as session:
        offset = (page - 1) * page_size
        total = len(session.exec(select(Author)).all())
        authors = session.exec(
            select(Author).offset(offset).limit(page_size)
        ).all()
        return {
            "items": authors,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

# Cette route sera destinée à rechercher des auteurs selon des critères que l'on lui apporte en json
@router.get("/search/")
def search_authors(
    name: str | None = None,
    country: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
    sort_by: str = Query(default="lastname"),
    order: str = Query(default="asc"),
):
    with Session(engine) as session:
        query = select(Author)
        
        if name:
            query = query.where(
                (Author.firstname.ilike(f"%{name}%")) | (Author.lastname.ilike(f"%{name}%"))
            )
        if country:
            query = query.where(Author.country == country)
        
        if sort_by == "lastname":
            query = query.order_by(Author.lastname.asc() if order == "asc" else Author.lastname.desc())
        elif sort_by == "firstname":
            query = query.order_by(Author.firstname.asc() if order == "asc" else Author.firstname.desc())
        elif sort_by == "birth":
            query = query.order_by(Author.birth.asc() if order == "asc" else Author.birth.desc())
        
        offset = (page - 1) * page_size
        total = len(session.exec(query).all())
        authors = session.exec(query.offset(offset).limit(page_size)).all()
        
        return {
            "items": authors,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

# Cette route sera destinée à créer un nouvel auteur dans la base de données en lui apportant toutes les clés nécessaires dans le JSON
@router.post("/", response_model=Author)
def create_author(author: Author):
    with Session(engine) as session:
        author.birth = formatage_date(author.birth, "birth")
        author.death = formatage_date(author.death, "death")

        exists = session.exec(
            select(Author).where(
                Author.firstname == author.firstname,
                Author.lastname == author.lastname,
            )
        ).first()
        if exists:
            raise HTTPException(409, "Cet auteur existe déjà")

        session.add(author)
        session.commit()
        session.refresh(author)
        return author

#Cette route sera destinée à récupérer toutes les informations disponibles pour un auteur spectifique
@router.get("/{author_id}")
def read_author(author_id: int):
    with Session(engine) as session:
        author = session.get(Author, author_id)
        if not author:
            raise HTTPException(404, "L'auteur est introuvable dans la base de données")
        
        books = session.exec(
            select(Book).where(Book.author_id == author_id)
        ).all()
        
        return {
            "author": author,
            "books": books,
        }


@router.patch("/{author_id}", response_model=Author)
def update_author(author_id: int, author: Author):
    with Session(engine) as session:
        db_author = session.get(Author, author_id)
        if not db_author:
            raise HTTPException(404, "L'auteur est introuvable dans la base de données")

        author_data = author.model_dump(exclude_unset=True)
        for key, value in author_data.items():
            if key in ("birth", "death"):
                value = formatage_date(value, key)
            setattr(db_author, key, value)

        session.add(db_author)
        session.commit()
        session.refresh(db_author)
        return db_author

# Cette route sera destinée à supprimer un auteur
@router.delete("/{author_id}")
def delete_author(author_id: int):
    with Session(engine) as session:
        author = session.get(Author, author_id)
        if not author:
            raise HTTPException(404, "Auteur introuvable")
        
        books = session.exec(
            select(Book).where(Book.author_id == author_id)
        ).first()
        if books:
            raise HTTPException(400, "Impossible de supprimer un auteur avec des livres associés")
        
        session.delete(author)
        session.commit()
        return {"message": "Auteur supprimé avec succès"}