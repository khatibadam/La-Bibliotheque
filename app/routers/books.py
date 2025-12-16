# app/routers/books.py
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from app.models import Book, Author
from app.database import engine

router = APIRouter(
    prefix="/books",
    tags=["Livres"]
)

# Cette route sera destinée à créer un livre dans la base de données
@router.post("/", response_model=Book)
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
@router.get("/")
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

# Cette route sera destinée à rechercher des livres selon des critères que l'on lui apporte en json
@router.get("/search/")
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

# Cette route sera destinée à lister tous les livres dans la base de données
@router.get("/{book_id}")
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
@router.patch("/{book_id}", response_model=Book)
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

# Cette route sera destinée à supprimer un auteur
@router.delete("/{book_id}")
def delete_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(404, "Livre introuvable")
        
        session.delete(book)
        session.commit()
        return {"message": "Livre supprimé avec succès"}