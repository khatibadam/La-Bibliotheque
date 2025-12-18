from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from datetime import date, timedelta, datetime
from app.database import engine
from app.models import Book, Loan

router = APIRouter(
    prefix="/loans",
    tags=["Emprunts"]
)

def today() -> date:
    return date.today()

# Fonction permettant de formater la date avant de la placer dans la base de données. Nécessaire car l'endpoint calcule une date (due_date) et il a besoin d’un type date, mais le start_date arrive encore comme texte à ce moment-là.
def parse_date(v, field_name: str) -> date:
    if v is None:
        return date.today()

    if isinstance(v, date) and not isinstance(v, datetime):
        return v

    if isinstance(v, datetime):
        return v.date()

    if isinstance(v, str):
        try:
            return date.fromisoformat(v)
        except ValueError as e:
            raise HTTPException(422, f"{field_name} doit être au format YYYY-MM-DD") from e
    raise HTTPException(422, f"{field_name} invalide")

def compute_due_date(start: date) -> date:
    return start + timedelta(days=28)

def compute_penalty(late_days: int) -> int:
    return max(0, late_days) * 50

# Cette route sera destinée à créer l'emprunt selon des critères que l'on lui apporte en json
@router.post("/", response_model=Loan)
def loan_book(loan: Loan):
    with Session(engine) as session:
        # On vérifie si le livre existe vraiment
        book = session.get(Book, loan.book_id)
        if not book:
            raise HTTPException(404, "Le livre est introuvable")

        # Si il y a plus de stocks, on renvoie un message
        if book.copies <= 0:
            raise HTTPException(409, "Plus de stocks pour ce livre")

        # On vérifie si l'utilisateur n'a pas atteint sa limite d'emprunts maximale en fonction de son mail ou de son card_id
        active_count = session.exec(
            select(Loan).where(
                Loan.active == True,
                (Loan.loaner_mail == loan.loaner_mail) | (Loan.loaner_card_id == loan.loaner_card_id)
            )
        ).all()
        if len(active_count) >= 5:
            raise HTTPException(403, "La limite d'emprunts a été atteinte pour cet utilisateur")

        # On construit le payload de l'emprunt avec la date du jour pour optenir la date de fin prévu
        start = parse_date(loan.start_date, "start_date")
        due = compute_due_date(start)

        loan = Loan(
            book_id=loan.book_id,
            loaner_name=loan.loaner_name,
            loaner_mail=loan.loaner_mail,
            loaner_card_id=loan.loaner_card_id,
            start_date=start,
            due_date=due,
            comment=loan.comment,
            active=True,
            renew_count=0,
            late_days=0,
            penalty_cents=0,
        )

        # On retire 1 des stocks du livre concerné si l'emprunt a bien été effectué
        book.copies -= 1

        session.add(book)
        session.add(loan)
        session.commit()
        session.refresh(loan)

        return loan

# Cette route sera destinée à marquer l'emprunt comme 'retourné' et le livre rapporté à la biblioteque
@router.post("/{loan_id}/return", response_model=Loan)
def return_book(loan_id: int):
    with Session(engine) as session:
        loan = session.get(Loan, loan_id)
        if not loan:
            raise HTTPException(404, "l'emprunt est introuvable")

        if not loan.active:
            raise HTTPException(409, "l'emprunt a déjà été retourné")

        book = session.get(Book, loan.book_id)
        if not book:
            raise HTTPException(500, "Aucun livre n'est disponible pour cet emprunt. Les données de la requête sont incohérentes")

        returned = today()
        late_days = max(0, (returned - loan.due_date).days)
        penalty = compute_penalty(late_days)

        loan.returned_date = returned
        loan.active = False
        loan.late_days = late_days
        loan.penalty_cents = penalty

        # On ajoute 1 des stocks du livre concerné si l'emprunt a bien été retrouné
        book.copies += 1

        session.add(book)
        session.add(loan)
        session.commit()
        session.refresh(loan)
        return loan

# Cette route sera destinée à lister les emprunts actifs, en retard et lister l'historique complet des emprunts 
@router.get("/")
def list_loans(
    status: str = Query(default="active", description="active, late ou history"),
    loaner_mail: str | None = None,
    loaner_card_id: int | None = None,
    book_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="start_date", description="active, late ou history"),
    order: str = Query(default="desc", description="asc ou desc"),
):
    with Session(engine) as session:
        q = select(Loan)

        # Filtrer par utilisateurs
        if loaner_mail:
            q = q.where(Loan.loaner_mail == loaner_mail)
        if loaner_card_id is not None:
            q = q.where(Loan.loaner_card_id == loaner_card_id)

        # Filtrer par livres
        if book_id is not None:
            q = q.where(Loan.book_id == book_id)

        # Filtrer par périodes
        if date_from:
            q = q.where(Loan.start_date >= date_from)
        if date_to:
            q = q.where(Loan.start_date <= date_to)

        # Filtrer par status
        if status == "active":
            q = q.where(Loan.active == True)
        elif status == "late":
            q = q.where(Loan.active == True, Loan.due_date < today())
        elif status == "history":
            q = q.where(Loan.active == False)
        else:
            raise HTTPException(422, "Le status doit être: active, late ou history")

        # le tri
        sort_col = {
            "start_date": Loan.start_date,
            "due_date": Loan.due_date,
            "returned_date": Loan.returned_date,
        }.get(sort_by)

        if not sort_col:
            raise HTTPException(422, "le sort_by est invalide")

        if order == "asc":
            q = q.order_by(sort_col.asc())
        elif order == "desc":
            q = q.order_by(sort_col.desc())
        else:
            raise HTTPException(422, "order doit être: asc ou desc")

        # la pagination
        offset = (page - 1) * page_size
        total = len(session.exec(q).all())
        items = session.exec(q.offset(offset).limit(page_size)).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

# Cette route sera destinée à laisser la posibilité de prolonger de 14 jours max un emprunt.
@router.post("/{loan_id}/renew", response_model=Loan)
def renew_loan(loan_id: int):
    with Session(engine) as session:
        loan = session.get(Loan, loan_id)
        if not loan:
            raise HTTPException(404, "L'emprunt est introuvable")

        if not loan.active:
            raise HTTPException(409, "L'emprunt a déjà été retourné. Imposible de le renouveller")

        if loan.renew_count >= 1:
            raise HTTPException(403, "le quôta de 1 renouvellement a déjà été utilisé par cet emprunt")

        # On ajoute les 14 jours à la date de retour
        loan.due_date = loan.due_date + timedelta(days=14)
        loan.renew_count += 1

        session.add(loan)
        session.commit()
        session.refresh(loan)
        return loan