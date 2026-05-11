from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.schemas import Caja, CajaCreate, CajaUpdate
from database import db, get_next_sequence
from datetime import datetime
from pymongo import ASCENDING, DESCENDING

router = APIRouter()

@router.get("/", response_model=List[Caja])
async def get_cajas(activa_only: bool = False):
    """Obtener todas las cajas"""
    try:
        mongo_filter = {}
        if activa_only:
            mongo_filter["activa"] = True

        cajas = list(db.cajas.find(mongo_filter, {"_id": 0}).sort("nombre", ASCENDING))
        return cajas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{caja_id}", response_model=Caja)
async def get_caja(caja_id: int):
    """Obtener una caja por ID"""
    try:
        caja = db.cajas.find_one({"id": caja_id}, {"_id": 0})

        if not caja:
            raise HTTPException(status_code=404, detail="Caja no encontrada")

        return caja
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Caja, status_code=201)
async def create_caja(caja: CajaCreate):
    """Crear una nueva caja"""
    try:
        existing = db.cajas.find_one({"nombre": caja.nombre}, {"_id": 0, "id": 1})
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una caja con ese nombre")

        caja_dict = caja.model_dump()
        caja_dict["id"] = get_next_sequence("cajas")
        caja_dict["created_at"] = datetime.utcnow()
        db.cajas.insert_one(caja_dict)

        if not caja_dict:
            raise HTTPException(status_code=400, detail="Error al crear la caja")

        caja_dict.pop("_id", None)
        return caja_dict
    except HTTPException:
        raise
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Ya existe una caja con ese nombre")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{caja_id}", response_model=Caja)
async def update_caja(caja_id: int, caja_update: CajaUpdate):
    """Actualizar una caja"""
    try:
        # Verificar que la caja existe
        check = db.cajas.find_one({"id": caja_id}, {"_id": 0, "id": 1})
        if not check:
            raise HTTPException(status_code=404, detail="Caja no encontrada")

        # Actualizar solo los campos proporcionados
        update_data = caja_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")

        db.cajas.update_one({"id": caja_id}, {"$set": update_data})
        updated = db.cajas.find_one({"id": caja_id}, {"_id": 0})

        if not updated:
            raise HTTPException(status_code=400, detail="Error al actualizar la caja")

        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{caja_id}")
async def delete_caja(caja_id: int):
    """Eliminar una caja (soft delete - marcar como inactiva)"""
    try:
        # Verificar que la caja existe
        check = db.cajas.find_one({"id": caja_id}, {"_id": 0, "id": 1})
        if not check:
            raise HTTPException(status_code=404, detail="Caja no encontrada")

        # Marcar como inactiva en lugar de eliminar
        result = db.cajas.update_one({"id": caja_id}, {"$set": {"activa": False}})

        if result.matched_count == 0:
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
        caja_info = db.cajas.find_one({"id": caja_id}, {"_id": 0, "id": 1, "nombre": 1, "saldo_inicial": 1})
        if not caja_info:
            raise HTTPException(status_code=404, detail="Caja no encontrada")

        # Obtener la última operación de caja
        result = db.cash_operations.find_one(
            {"caja_id": caja_id},
            {"_id": 0, "saldo": 1},
            sort=[("fecha", DESCENDING), ("id", DESCENDING)],
        )

        if result:
            saldo = result["saldo"]
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
        check = db.cajas.find_one({"id": caja_id}, {"_id": 0, "id": 1})
        if not check:
            raise HTTPException(status_code=404, detail="Caja no encontrada")

        result = list(db.products.find({"caja_id": caja_id}, {"_id": 0}).sort("name", ASCENDING))

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
