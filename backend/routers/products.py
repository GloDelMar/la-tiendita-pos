from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from models.schemas import Product, ProductCreate, ProductUpdate
from database import supabase
import uuid

router = APIRouter()

@router.get("/", response_model=List[Product])
async def get_all_products(caja_id: Optional[int] = None):
    """Obtener todos los productos, opcionalmente filtrados por caja"""
    try:
        query = supabase.table("products").select("*").order("name")
        
        if caja_id is not None:
            query = query.eq("caja_id", caja_id)
        
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Obtener un producto por ID"""
    try:
        response = supabase.table("products").select("*").eq("id", product_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener producto: {str(e)}")

@router.post("/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    """Crear un nuevo producto"""
    try:
        product_dict = product.model_dump()
        print(f"[DEBUG] Creating product with data: {product_dict}")
        response = supabase.table("products").insert(product_dict).execute()
        print(f"[DEBUG] Supabase response: {response}")
        return response.data[0]
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
        existing = supabase.table("products").select("*").eq("id", product_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Actualizar solo campos proporcionados
        update_dict = product.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        response = supabase.table("products").update(update_dict).eq("id", product_id).execute()
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar producto: {str(e)}")

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int):
    """Eliminar un producto"""
    try:
        existing = supabase.table("products").select("*").eq("id", product_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Eliminar imagen si existe
        if existing.data[0].get("image_url"):
            image_path = existing.data[0]["image_url"].split("/")[-1]
            try:
                supabase.storage.from_("product-images").remove([image_path])
            except:
                pass  # Continuar aunque falle el borrado de imagen
        
        supabase.table("products").delete().eq("id", product_id).execute()
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
        existing = supabase.table("products").select("*").eq("id", product_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Generar nombre único
        ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_name = f"{product_id}_{uuid.uuid4()}.{ext}"
        
        # Subir a Supabase Storage
        file_bytes = await file.read()
        storage_response = supabase.storage.from_("product-images").upload(
            unique_name, 
            file_bytes,
            {"content-type": file.content_type}
        )
        
        # Obtener URL pública
        public_url = supabase.storage.from_("product-images").get_public_url(unique_name)
        
        # Actualizar producto con nueva URL
        supabase.table("products").update({"image_url": public_url}).eq("id", product_id).execute()
        
        return {"image_url": public_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")
