# app/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import model_validator
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import date
import os
from dotenv import load_dotenv

# Les infos de base de l'API
app = FastAPI(
    title="La Bibliothèque",
    description="API REST dédiée à la gestion des livres, des auteurs, des emprunts et un système de recherche avancé",
    version="1.0.0",
)

# On définit les classes Book + Author afin d'être exploitées par les tables
class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    isbn: str = Field(unique=True)
    year: int
    author_id: int
    copies: int = Field(default=0, ge=0)
    owned: int = Field(default=0, gt=0)
    description: str | None = None
    category: str | None = None
    language: str
    pages: int = Field(gt=0)
    house: str | None = None

    @model_validator(mode="after")
    def copies_over_owned(self):
        if self.copies > self.owned:
            raise ValueError("Le nombre d'exemplaires ne peut pas dépasser le total possédé")
        return self

class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    birth: date
    country: str
    bio: str | None = None
    death: date | None = None
    website: str | None = None

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

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# On définit toutes les routes API ainsi que leurs utilités 
# On définit un message de bienvenue pour la route root
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de La Bibliothèque"}

# Cette route sera destinée à créer un livre dans la base de données
@app.post("/books/", response_model=Book)
def create_book(book: Book):
    with Session(engine) as session:
        exists_isbn = session.exec(
            select(Book).where(Book.isbn == book.isbn)
        ).first()
        if exists_isbn:
            raise HTTPException(409, "Un livre avec cet ISBN existe déjà")
        
        author = session.get(Author, book.author_id)
        if not author:
            raise HTTPException(404, "L'auteur référencé n'existe pas")
        
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

# Cette route sera destinée à lister tous les livres dans la base de données
@app.get("/books/")
def read_books(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
    sort_by: str = Query(default="title"),
    order: str = Query(default="asc"),
):
    with Session(engine) as session:
        offset = (page - 1) * page_size
        
        query = select(Book)
        if sort_by == "title":
            query = query.order_by(Book.title.asc() if order == "asc" else Book.title.desc())
        elif sort_by == "year":
            query = query.order_by(Book.year.asc() if order == "asc" else Book.year.desc())
        elif sort_by == "author":
            query = query.order_by(Book.author_id.asc() if order == "asc" else Book.author_id.desc())
        
        total = len(session.exec(select(Book)).all())
        books = session.exec(query.offset(offset).limit(page_size)).all()
        
        return {
            "items": books,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

# Cette route sera destinée à récupérer toutes les informations d'un livre donné
def read_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(404, "Livre introuvable")
        
        author = session.get(Author, book.author_id)
        
        return {
            "book": book,
            "author": author,
        }
    
# Cette route sera destinée à mettre à jour les informations d'un livre existant
@app.patch("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: Book):
    with Session(engine) as session:
        db_book = session.get(Book, book_id)
        if not db_book:
            raise HTTPException(404, "Livre introuvable")
        
        book_data = book.model_dump(exclude_unset=True)
        for key, value in book_data.items():
            setattr(db_book, key, value)
        
        session.add(db_book)
        session.commit()
        session.refresh(db_book)
        return db_book

# Cette route sera destinée à supprimer un livre du catalogue
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(404, "Livre introuvable")
        
        session.delete(book)
        session.commit()
        return {"message": "Livre supprimé avec succès"}

# Cette route sera destinée à rechercher des livres selon des critères que l'on lui apporte en json
@app.get("/books/search/")
def search_books(
    title: str | None = None,
    author_name: str | None = None,
    isbn: str | None = None,
    category: str | None = None,
    year: int | None = None,
    language: str | None = None,
    available: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
):
    with Session(engine) as session:
        query = select(Book)
        
        if title:
            query = query.where(Book.title.ilike(f"%{title}%"))
        if isbn:
            query = query.where(Book.isbn == isbn)
        if category:
            query = query.where(Book.category == category)
        if year:
            query = query.where(Book.year == year)
        if language:
            query = query.where(Book.language == language)
        if available is not None:
            if available:
                query = query.where(Book.copies > 0)
            else:
                query = query.where(Book.copies == 0)
        
        if author_name:
            authors = session.exec(
                select(Author).where(
                    (Author.firstname.ilike(f"%{author_name}%")) | 
                    (Author.lastname.ilike(f"%{author_name}%"))
                )
            ).all()
            author_ids = [author.id for author in authors]
            if author_ids:
                query = query.where(Book.author_id.in_(author_ids))
        
        offset = (page - 1) * page_size
        total = len(session.exec(query).all())
        books = session.exec(query.offset(offset).limit(page_size)).all()
        
        return {
            "items": books,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

# Cette route sera destinée à lister tous les auteurs disponibles dans la base de données
@app.get("/authors/")
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

# Cette route sera destinée à créer un nouvel auteur dans la base de données en lui apportant toutes les clés nécessaires dans le JSON
@app.post("/authors/", response_model=Author)
def create_author(author: Author):
    with Session(engine) as session:
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
@app.get("/authors/{author_id}")
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

# Cette route sera destinée à modifier les informations d'un auteur
@app.patch("/authors/{author_id}", response_model=Author)
def update_author(author_id: int, author: Author):
    with Session(engine) as session:
        db_author = session.get(Author, author_id)
        if not db_author:
            raise HTTPException(404, "L'auteur est introuvable dans la base de données")
        
        author_data = author.model_dump(exclude_unset=True)
        for key, value in author_data.items():
            setattr(db_author, key, value)
        
        session.add(db_author)
        session.commit()
        session.refresh(db_author)
        return db_author

# Cette route sera destinée à supprimer un auteur
@app.delete("/authors/{author_id}")
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

# Cette route sera destinée à rechercher des auteurs selon des critères que l'on lui apporte en json
@app.get("/authors/search/")
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