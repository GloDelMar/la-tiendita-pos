from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.schemas import Debtor, DebtorCreate, DebtorUpdate, PaymentResponse
from database import supabase

router = APIRouter()

@router.get("/", response_model=List[Debtor])
async def get_all_debtors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    grupo: Optional[str] = None,
    nombre: Optional[str] = None
):
    """Obtener todos los deudores con filtros opcionales"""
    try:
        query = supabase.table("debtors").select("*")
        
        if grupo:
            query = query.eq("grupo", grupo)
        if nombre:
            query = query.ilike("nombre", f"%{nombre}%")
        
        response = query.order("deuda", desc=True).range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener deudores: {str(e)}")

@router.get("/{debtor_id}", response_model=Debtor)
async def get_debtor(debtor_id: int):
    """Obtener un deudor por ID"""
    try:
        response = supabase.table("debtors").select("*").eq("id", debtor_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Deudor no encontrado")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener deudor: {str(e)}")

@router.get("/by-name/{nombre}/{grupo}", response_model=Debtor)
async def get_debtor_by_name(nombre: str, grupo: str):
    """Obtener un deudor por nombre y grupo"""
    try:
        response = supabase.table("debtors").select("*").eq("nombre", nombre).eq("grupo", grupo).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Deudor no encontrado")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener deudor: {str(e)}")

@router.post("/", response_model=Debtor, status_code=201)
async def create_debtor(debtor: DebtorCreate):
    """Crear un nuevo deudor"""
    try:
        # Verificar si ya existe
        existing = supabase.table("debtors").select("*").eq("nombre", debtor.nombre).eq("grupo", debtor.grupo).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="El deudor ya existe")
        
        debtor_dict = debtor.model_dump()
        response = supabase.table("debtors").insert(debtor_dict).execute()
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear deudor: {str(e)}")

@router.patch("/{debtor_id}/pay", response_model=PaymentResponse)
async def pay_debt(debtor_id: int, monto: float = Query(..., gt=0)):
    """Registrar pago de deuda"""
    try:
        # Obtener deudor actual
        existing = supabase.table("debtors").select("*").eq("id", debtor_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Deudor no encontrado")
        
        debtor = existing.data[0]
        nueva_deuda = debtor["deuda"] - monto
        
        if nueva_deuda < 0:
            raise HTTPException(status_code=400, detail="El monto excede la deuda")
        
        # Si la deuda queda en 0, eliminar el deudor
        if nueva_deuda == 0:
            supabase.table("debtors").delete().eq("id", debtor_id).execute()
            
            # Registrar en caja el pago
            last_operation = supabase.table("cash_operations").select("*").order("fecha", desc=True).limit(1).execute()
            current_balance = last_operation.data[0]["saldo"] if last_operation.data else 0
            
            cash_operation = {
                "tipo_operacion": "INGRESO",
                "monto": monto,
                "saldo": current_balance + monto,
                "descripcion": f"Pago de deuda - {debtor['nombre']} ({debtor['grupo']}) - Saldada completamente"
            }
            supabase.table("cash_operations").insert(cash_operation).execute()
            
            return PaymentResponse(
                mensaje="Deuda saldada completamente",
                deuda_restante=0,
                debtor=None
            )
        else:
            # Actualizar deuda
            response = supabase.table("debtors").update({"deuda": nueva_deuda}).eq("id", debtor_id).execute()
            
            # Registrar en caja el pago
            last_operation = supabase.table("cash_operations").select("*").order("fecha", desc=True).limit(1).execute()
            current_balance = last_operation.data[0]["saldo"] if last_operation.data else 0
            
            cash_operation = {
                "tipo_operacion": "INGRESO",
                "monto": monto,
                "saldo": current_balance + monto,
                "descripcion": f"Pago parcial de deuda - {debtor['nombre']} ({debtor['grupo']}) - Resta ${nueva_deuda:.2f}"
            }
            supabase.table("cash_operations").insert(cash_operation).execute()
            
            return PaymentResponse(
                mensaje="Pago registrado exitosamente",
                deuda_restante=nueva_deuda,
                debtor=response.data[0]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar pago: {str(e)}")

@router.put("/{debtor_id}", response_model=Debtor)
async def update_debtor(debtor_id: int, debtor: DebtorUpdate):
    """Actualizar deuda manualmente"""
    try:
        existing = supabase.table("debtors").select("*").eq("id", debtor_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Deudor no encontrado")
        
        update_dict = debtor.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        response = supabase.table("debtors").update(update_dict).eq("id", debtor_id).execute()
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar deudor: {str(e)}")

@router.delete("/{debtor_id}", status_code=204)
async def delete_debtor(debtor_id: int):
    """Eliminar un deudor (condonar deuda)"""
    try:
        existing = supabase.table("debtors").select("*").eq("id", debtor_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Deudor no encontrado")
        
        supabase.table("debtors").delete().eq("id", debtor_id).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar deudor: {str(e)}")

@router.get("/stats/summary")
async def get_debtors_summary():
    """Obtener resumen de deudas"""
    try:
        debtors = supabase.table("debtors").select("*").execute()
        
        total_deuda = sum(d["deuda"] for d in debtors.data)
        
        # Agrupar por grupo
        grupos = {}
        for debtor in debtors.data:
            grupo = debtor["grupo"]
            if grupo not in grupos:
                grupos[grupo] = {"cantidad": 0, "total": 0}
            grupos[grupo]["cantidad"] += 1
            grupos[grupo]["total"] += debtor["deuda"]
        
        return {
            "total_deudores": len(debtors.data),
            "total_deuda": total_deuda,
            "promedio_deuda": total_deuda / len(debtors.data) if debtors.data else 0,
            "por_grupo": grupos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen: {str(e)}")
