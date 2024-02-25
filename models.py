from beanie import Document
from pydantic import BaseModel
from typing import List

class Reporter(BaseModel):
    FullName: str
    Email: str

class Approver(BaseModel):
    FullName: str
    Email: str

class Transaction(BaseModel):
    Date: str
    Type: str
    Amount: float
    Currency: str
    Reference: str
    Details: str

class Details(BaseModel):
    CreatedAt: str
    Status: str

class Invoice(Document):
    ID: str
    Details: Details
    Reporter: Reporter
    Approvers: List[Approver]
    Transactions: List[Transaction]

    class Settings:
        name ="invoices"
        
