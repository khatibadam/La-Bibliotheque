# app/models.py
from sqlmodel import Field, SQLModel
from pydantic import model_validator
from datetime import date

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