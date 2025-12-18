# app/models.py
from sqlmodel import Field, SQLModel
from pydantic import model_validator, field_validator
from datetime import date, datetime

# On définit les classes Book, Author et Loan afin que l'api puisse écrire les données dans les tables

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

    @field_validator("birth", "death", mode="before")
    @classmethod
    # Fonction permettant de formater la date avant de la placer dans la base de données. Nécessaire car sinon nous avons l'erreur 'SQLite Date type only accepts Python date objects as input.'
    def parse_dates(cls, v):
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
                try:
                    return datetime.strptime(v, "%d/%m/%Y").date()
                except ValueError as e:
                    raise ValueError("Format de date invalide. Utilise 'YYYY-MM-DD' (ex: 1985-04-12).") from e
        raise TypeError("La date doit être une date, un datetime, ou une string 'YYYY-MM-DD'.")

class Loan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    book_id: int = Field(index=True)
    loaner_name: str
    loaner_mail: str = Field(index=True)
    loaner_card_id: int = Field(index=True)
    start_date: date
    due_date: date
    returned_date: date = Field(default=None, nullable=True)
    active: bool = Field(default=True)
    renew_count: int = Field(default=0, ge=0)
    late_days: int = Field(default=0, ge=0)
    penalty_cents: int = Field(default=0, ge=0)
    comment: str | None = None