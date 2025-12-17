# app/routers/loans.py
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from app.models import Book, Loan
from app.database import engine

router = APIRouter(
    prefix="/loans",
    tags=["Prêts"]
)

# Cette route sera destinée à lister tous les prêts effectués dans la base de données
@router.get("/")
def read_loans(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
):
    with Session(engine) as session:
        offset = (page - 1) * page_size
        total = len(session.exec(select(Loan)).all())
        loans = session.exec(
            select(Loan).offset(offset).limit(page_size)
        ).all()
        return {
            "items": loans,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

# Cette route sera destinée à rechercher des prêts selon des critères que l'on lui apporte en json
@router.get("/search/")
def search_loan(
    name: str | None = None,
    country: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
    sort_by: str = Query(default="lastname"),
    order: str = Query(default="asc"),
):
    with Session(engine) as session:
        query = select(Loan)
        
        if name:
            query = query.where(
                (Loan.firstname.ilike(f"%{name}%")) | (Loan.lastname.ilike(f"%{name}%"))
            )
        if country:
            query = query.where(Loan.country == country)
        
        if sort_by == "lastname":
            query = query.order_by(Loan.lastname.asc() if order == "asc" else Loan.lastname.desc())
        elif sort_by == "firstname":
            query = query.order_by(Loan.firstname.asc() if order == "asc" else Loan.firstname.desc())
        elif sort_by == "birth":
            query = query.order_by(Loan.birth.asc() if order == "asc" else Loan.birth.desc())
        
        offset = (page - 1) * page_size
        total = len(session.exec(query).all())
        Loans = session.exec(query.offset(offset).limit(page_size)).all()
        
        return {
            "items": Loans,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

# Cette route sera destinée à créer un nouvel auteur dans la base de données en lui apportant toutes les clés nécessaires dans le JSON
@router.post("/", response_model=Loan)
def create_loan(Loan: Loan):
    with Session(engine) as session:
        exists = session.exec(
            select(Loan).where(
                Loan.firstname == Loan.firstname,
                Loan.lastname == Loan.lastname,
            )
        ).first()
        if exists:
            raise HTTPException(409, "Cet auteur existe déjà")

        session.add(Loan)
        session.commit()
        session.refresh(Loan)
        return Loan

#Cette route sera destinée à récupérer toutes les informations disponibles pour un auteur spectifique
@router.get("/{Loan_id}")
def read_loan(Loan_id: int):
    with Session(engine) as session:
        Loan = session.get(Loan, Loan_id)
        if not Loan:
            raise HTTPException(404, "L'auteur est introuvable dans la base de données")
        
        books = session.exec(
            select(Book).where(Book.Loan_id == Loan_id)
        ).all()
        
        return {
            "Loan": Loan,
            "books": books,
        }


@router.patch("/{Loan_id}", response_model=Loan)
def update_loan(Loan_id: int, Loan: Loan):
    with Session(engine) as session:
        db_Loan = session.get(Loan, Loan_id)
        if not db_Loan:
            raise HTTPException(404, "L'auteur est introuvable dans la base de données")
        
        Loan_data = Loan.model_dump(exclude_unset=True)
        for key, value in Loan_data.items():
            setattr(db_Loan, key, value)
        
        session.add(db_Loan)
        session.commit()
        session.refresh(db_Loan)
        return db_Loan

# Cette route sera destinée à supprimer un auteur
@router.delete("/{Loan_id}")
def delete_loan(Loan_id: int):
    with Session(engine) as session:
        Loan = session.get(Loan, Loan_id)
        if not Loan:
            raise HTTPException(404, "Auteur introuvable")
        
        books = session.exec(
            select(Book).where(Book.Loan_id == Loan_id)
        ).first()
        if books:
            raise HTTPException(400, "Impossible de supprimer un auteur avec des livres associés")
        
        session.delete(Loan)
        session.commit()
        return {"message": "Auteur supprimé avec succès"}