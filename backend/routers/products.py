from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from models.schemas import Product, ProductCreate, ProductUpdate
from database import db, get_next_sequence
from pymongo import ASCENDING
import uuid
from pathlib import Path
from datetime import datetime

router = APIRouter()


def _serialize(doc: Optional[dict]) -> Optional[dict]:
    if not doc:
        return None
    doc.pop("_id", None)
    return doc

@router.get("/", response_model=List[Product])
async def get_all_products(caja_id: Optional[int] = None):
    """Obtener todos los productos, opcionalmente filtrados por caja"""
    try:
        query = {}
        if caja_id is not None:
            query["caja_id"] = caja_id

        products = list(db.products.find(query, {"_id": 0}).sort("name", ASCENDING))
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Obtener un producto por ID"""
    try:
        product = db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener producto: {str(e)}")

@router.post("/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    """Crear un nuevo producto"""
    try:
        product_dict = product.model_dump()
        product_dict["id"] = get_next_sequence("products")
        product_dict["created_at"] = datetime.utcnow()
        print(f"[DEBUG] Creating product with data: {product_dict}")
        db.products.insert_one(product_dict)
        print("[DEBUG] Mongo insert completed")
        return _serialize(product_dict)
    except Exception as e:
        print(f"[ERROR] Exception creating product: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(e)}")

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductUpdate):
    """Actualizar un producto existente"""
    try:
        # Verificar que existe
        existing = db.products.find_one({"id": product_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Actualizar solo campos proporcionados
        update_dict = product.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        db.products.update_one({"id": product_id}, {"$set": update_dict})
        updated = db.products.find_one({"id": product_id}, {"_id": 0})
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar producto: {str(e)}")

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int):
    """Eliminar un producto"""
    try:
        existing = db.products.find_one({"id": product_id}, {"_id": 0})
        if not existing:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Eliminar imagen si existe
        if existing.get("image_url"):
            image_path = existing["image_url"].split("/")[-1]
            try:
                image_file = Path(__file__).resolve().parents[1] / "uploads" / "products" / image_path
                if image_file.exists():
                    image_file.unlink()
            except:
                pass  # Continuar aunque falle el borrado de imagen

        db.products.delete_one({"id": product_id})
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar producto: {str(e)}")

@router.post("/upload-image/{product_id}")
async def upload_product_image(product_id: int, file: UploadFile = File(...)):
    """Subir imagen para un producto"""
    try:
        # Verificar que el producto existe
        existing = db.products.find_one({"id": product_id}, {"_id": 0})
        if not existing:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

        # Generar nombre único
        ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_name = f"{product_id}_{uuid.uuid4()}.{ext}"

        # Guardar archivo localmente
        uploads_dir = Path(__file__).resolve().parents[1] / "uploads" / "products"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        file_bytes = await file.read()
        target_file = uploads_dir / unique_name
        target_file.write_bytes(file_bytes)

        # URL pública servida por FastAPI
        public_url = f"/static/products/{unique_name}"

        # Actualizar producto con nueva URL
        db.products.update_one({"id": product_id}, {"$set": {"image_url": public_url}})

        return {"image_url": public_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")
