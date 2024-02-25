from fastapi import FastAPI
from routes import invoice_router
from database import init_db

app=FastAPI()

@app.on_event("startup")
async def connect():
    await init_db()

app.include_router(invoice_router, prefix="/invoices")
