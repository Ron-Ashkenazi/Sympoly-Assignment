from fastapi import APIRouter, UploadFile, File, HTTPException
from models import Invoice
from typing import Dict, Any
from functions import read_file
import json

invoice_router = APIRouter()

@invoice_router.get("/")
async def getAllInvoices() -> Dict[str, Any]:
    try:
        invoices = await Invoice.find_all().to_list()
        result = {
            "numOfInvoices": len(invoices),
            "invoices": invoices
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.post("/")
async def createInvoice(text_file: UploadFile = File(...)):
    try:
        if not text_file.filename.endswith('.exrf'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only .exrf files are allowed.")

        contents = await text_file.read()

        result = read_file(contents.decode())

        result_dict = json.loads(result)
        result_object = Invoice(**result_dict)
        await result_object.create()

        return {"message": "Invoice has been saved", "new_invoice": result_object}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.get("/{invoice_id}")
async def retriveInvoice(invoice_id: str):
    try:
        invoice_to_get = await Invoice.find_one({"ID": invoice_id})
        if invoice_to_get:
            return invoice_to_get
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.delete("/{invoice_id}")
async def deleteInvoice(invoice_id: str):
    try:
        invoice_to_delete = await Invoice.find_one({"ID": invoice_id})
        if invoice_to_delete:
            await invoice_to_delete.delete()
            return {"message": "Invoice deleted"}
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
