from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.schemas import Caja, CajaCreate, CajaUpdate
from database import supabase

router = APIRouter()

@router.get("/", response_model=List[Caja])
async def get_cajas(activa_only: bool = False):
    """Obtener todas las cajas"""
    try:
        query = supabase.table("cajas").select("*").order("nombre")
        
        if activa_only:
            query = query.eq("activa", True)
        
        result = query.execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{caja_id}", response_model=Caja)
async def get_caja(caja_id: int):
    """Obtener una caja por ID"""
    try:
        result = supabase.table("cajas").select("*").eq("id", caja_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Caja, status_code=201)
async def create_caja(caja: CajaCreate):
    """Crear una nueva caja"""
    try:
        result = supabase.table("cajas").insert(caja.model_dump()).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Error al crear la caja")
        
        return result.data[0]
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Ya existe una caja con ese nombre")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{caja_id}", response_model=Caja)
async def update_caja(caja_id: int, caja_update: CajaUpdate):
    """Actualizar una caja"""
    try:
        # Verificar que la caja existe
        check = supabase.table("cajas").select("id").eq("id", caja_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        
        # Actualizar solo los campos proporcionados
        update_data = caja_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")
        
        result = supabase.table("cajas").update(update_data).eq("id", caja_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Error al actualizar la caja")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{caja_id}")
async def delete_caja(caja_id: int):
    """Eliminar una caja (soft delete - marcar como inactiva)"""
    try:
        # Verificar que la caja existe
        check = supabase.table("cajas").select("id").eq("id", caja_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        
        # Marcar como inactiva en lugar de eliminar
        result = supabase.table("cajas").update({"activa": False}).eq("id", caja_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Error al desactivar la caja")
        
        return {"message": "Caja desactivada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{caja_id}/saldo")
async def get_caja_saldo(caja_id: int):
    """Obtener el saldo actual de una caja"""
    try:
        # Verificar que la caja existe
        check = supabase.table("cajas").select("id, nombre, saldo_inicial").eq("id", caja_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        
        caja_info = check.data[0]
        
        # Obtener la última operación de caja
        result = supabase.table("cash_operations")\
            .select("saldo")\
            .eq("caja_id", caja_id)\
            .order("fecha", desc=True)\
            .order("id", desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            saldo = result.data[0]["saldo"]
        else:
            # Si no hay operaciones, usar el saldo inicial
            saldo = caja_info["saldo_inicial"]
        
        return {
            "caja_id": caja_id,
            "caja_nombre": caja_info["nombre"],
            "saldo": saldo
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{caja_id}/productos")
async def get_productos_por_caja(caja_id: int):
    """Obtener todos los productos de una caja específica"""
    try:
        # Verificar que la caja existe
        check = supabase.table("cajas").select("id").eq("id", caja_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        
        result = supabase.table("products")\
            .select("*")\
            .eq("caja_id", caja_id)\
            .order("name")\
            .execute()
        
        return result.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
