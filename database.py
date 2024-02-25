import beanie
import motor.motor_asyncio
from models import Invoice

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")

    db = client["invoice_database"]
    collection = db["invoices"]

    await collection.create_index("ID", unique=True)

    await beanie.init_beanie(
        database=db,
        document_models=[Invoice]
    )