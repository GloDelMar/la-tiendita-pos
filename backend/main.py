from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import products, transactions, debtors, cash, cajas
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="La Tiendita API",
    description="Point of Sale API for La Tiendita",
    version="1.0.0"
)

# CORS configuration - Allow all origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Vercel deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cajas.router, prefix="/api/cajas", tags=["cajas"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(debtors.router, prefix="/api/debtors", tags=["debtors"])
app.include_router(cash.router, prefix="/api/cash", tags=["cash"])

@app.get("/")
async def root():
    return {"message": "La Tiendita API - Point of Sale System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
