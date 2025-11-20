from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.schemas import CashOperation, CashOperationCreate
from database import supabase
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[CashOperation])
async def get_cash_operations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    tipo_operacion: Optional[str] = None,
    caja_id: Optional[int] = None
):
    """Obtener movimientos de caja con filtros opcionales"""
    try:
        query = supabase.table("cash_operations").select("*")
        
        if fecha_desde:
            query = query.gte("fecha", fecha_desde)
        if fecha_hasta:
            query = query.lte("fecha", fecha_hasta)
        if tipo_operacion:
            query = query.eq("tipo_operacion", tipo_operacion)
        if caja_id is not None:
            query = query.eq("caja_id", caja_id)
        
        response = query.order("fecha", desc=True).range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener operaciones: {str(e)}")

@router.get("/balance")
async def get_current_balance(caja_id: Optional[int] = None):
    """Obtener saldo actual de caja (todas o una específica)"""
    try:
        query = supabase.table("cash_operations").select("*")
        
        if caja_id is not None:
            query = query.eq("caja_id", caja_id)
        
        last_operation = query.order("fecha", desc=True).order("id", desc=True).limit(1).execute()
        
        if not last_operation.data:
            # Si no hay operaciones y es una caja específica, obtener saldo inicial
            if caja_id is not None:
                caja = supabase.table("cajas").select("saldo_inicial, nombre").eq("id", caja_id).execute()
                if caja.data:
                    return {
                        "saldo": caja.data[0]["saldo_inicial"],
                        "ultima_actualizacion": None,
                        "caja_id": caja_id,
                        "caja_nombre": caja.data[0]["nombre"]
                    }
            return {"saldo": 0, "ultima_actualizacion": None}
        
        result = {
            "saldo": last_operation.data[0]["saldo"],
            "ultima_actualizacion": last_operation.data[0]["fecha"]
        }
        
        if caja_id is not None:
            result["caja_id"] = caja_id
            caja = supabase.table("cajas").select("nombre").eq("id", caja_id).execute()
            if caja.data:
                result["caja_nombre"] = caja.data[0]["nombre"]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener saldo: {str(e)}")

@router.get("/{operation_id}", response_model=CashOperation)
async def get_cash_operation(operation_id: int):
    """Obtener una operación por ID"""
    try:
        response = supabase.table("cash_operations").select("*").eq("id", operation_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Operación no encontrada")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener operación: {str(e)}")

@router.post("/", response_model=CashOperation, status_code=201)
async def create_cash_operation(operation: CashOperationCreate):
    """Crear una nueva operación de caja (ingreso, egreso o ajuste)"""
    try:
        # Obtener saldo actual de la caja específica
        query = supabase.table("cash_operations").select("*").order("fecha", desc=True).order("id", desc=True).limit(1)
        
        if operation.caja_id is not None:
            query = query.eq("caja_id", operation.caja_id)
        
        last_operation = query.execute()
        
        # Si no hay operaciones previas y hay caja_id, usar saldo inicial de la caja
        if not last_operation.data and operation.caja_id is not None:
            caja = supabase.table("cajas").select("saldo_inicial").eq("id", operation.caja_id).execute()
            current_balance = caja.data[0]["saldo_inicial"] if caja.data else 0
        else:
            current_balance = last_operation.data[0]["saldo"] if last_operation.data else 0
        
        # Calcular nuevo saldo
        if operation.tipo_operacion in ["INGRESO", "VENTA"]:
            new_balance = current_balance + abs(operation.monto)
        elif operation.tipo_operacion == "EGRESO":
            new_balance = current_balance - abs(operation.monto)
        else:  # AJUSTE
            new_balance = current_balance + operation.monto
        
        # Crear operación
        operation_dict = operation.model_dump()
        operation_dict["saldo"] = new_balance
        
        response = supabase.table("cash_operations").insert(operation_dict).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear operación: {str(e)}")

@router.post("/income", response_model=CashOperation, status_code=201)
async def add_income(monto: float = Query(..., gt=0), descripcion: str = Query(...), caja_id: Optional[int] = None):
    """Registrar un ingreso de efectivo"""
    try:
        operation = CashOperationCreate(
            tipo_operacion="INGRESO",
            monto=monto,
            descripcion=descripcion,
            caja_id=caja_id
        )
        return await create_cash_operation(operation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar ingreso: {str(e)}")

@router.post("/expense", response_model=CashOperation, status_code=201)
async def add_expense(monto: float = Query(..., gt=0), descripcion: str = Query(...), caja_id: Optional[int] = None):
    """Registrar un egreso de efectivo"""
    try:
        operation = CashOperationCreate(
            tipo_operacion="EGRESO",
            monto=monto,
            descripcion=descripcion,
            caja_id=caja_id
        )
        return await create_cash_operation(operation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar egreso: {str(e)}")

@router.post("/adjust", response_model=CashOperation, status_code=201)
async def adjust_balance(monto: float = Query(...), descripcion: str = Query("Ajuste manual"), caja_id: Optional[int] = None):
    """Ajustar saldo de caja (positivo o negativo)"""
    try:
        operation = CashOperationCreate(
            tipo_operacion="AJUSTE",
            monto=monto,
            descripcion=descripcion,
            caja_id=caja_id
        )
        return await create_cash_operation(operation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ajustar saldo: {str(e)}")

@router.get("/stats/daily")
async def get_daily_cash_stats(fecha: Optional[str] = None, caja_id: Optional[int] = None):
    """Obtener estadísticas de caja del día"""
    try:
        if not fecha:
            fecha = datetime.now().strftime("%Y-%m-%d")
        
        fecha_inicio = f"{fecha}T00:00:00"
        fecha_fin = f"{fecha}T23:59:59"
        
        print(f"[DEBUG] getDailyStats - fecha: {fecha}, caja_id: {caja_id}")
        print(f"[DEBUG] Rango: {fecha_inicio} a {fecha_fin}")
        
        query = supabase.table("cash_operations").select("*").gte("fecha", fecha_inicio).lte("fecha", fecha_fin)
        if caja_id is not None:
            query = query.eq("caja_id", caja_id)
        operations = query.execute()
        
        print(f"[DEBUG] Operaciones encontradas: {len(operations.data)}")
        if operations.data:
            print(f"[DEBUG] Primera operación: {operations.data[0]}")
        
        ingresos = sum(op["monto"] for op in operations.data if op["tipo_operacion"] in ["INGRESO", "VENTA"] and op["monto"] > 0)
        egresos = sum(abs(op["monto"]) for op in operations.data if op["tipo_operacion"] == "EGRESO")
        ajustes = sum(op["monto"] for op in operations.data if op["tipo_operacion"] == "AJUSTE")
        
        print(f"[DEBUG] ingresos: {ingresos}, egresos: {egresos}, ajustes: {ajustes}")
        
        # Saldo al inicio del día
        query_before = supabase.table("cash_operations").select("*").lt("fecha", fecha_inicio)
        if caja_id is not None:
            query_before = query_before.eq("caja_id", caja_id)
        operations_before = query_before.order("fecha", desc=True).limit(1).execute()
        
        # Si no hay operaciones previas y hay caja_id, usar saldo inicial de la caja
        if not operations_before.data and caja_id is not None:
            caja = supabase.table("cajas").select("saldo_inicial").eq("id", caja_id).execute()
            saldo_inicial = caja.data[0]["saldo_inicial"] if caja.data else 0
        else:
            saldo_inicial = operations_before.data[0]["saldo"] if operations_before.data else 0
        
        # Saldo actual
        query_current = supabase.table("cash_operations").select("*")
        if caja_id is not None:
            query_current = query_current.eq("caja_id", caja_id)
        current = query_current.order("fecha", desc=True).limit(1).execute()
        saldo_actual = current.data[0]["saldo"] if current.data else saldo_inicial
        
        return {
            "fecha": fecha,
            "saldo_inicial": saldo_inicial,
            "ingresos": ingresos,
            "egresos": egresos,
            "ajustes": ajustes,
            "saldo_actual": saldo_actual,
            "diferencia": saldo_actual - saldo_inicial
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.delete("/{operation_id}", status_code=204)
async def delete_cash_operation(operation_id: int):
    """Eliminar una operación de caja (requiere recalcular saldos)"""
    try:
        # Obtener la operación a eliminar
        operation = supabase.table("cash_operations").select("*").eq("id", operation_id).execute()
        if not operation.data:
            raise HTTPException(status_code=404, detail="Operación no encontrada")
        
        # Esta es una operación compleja que requiere recalcular todos los saldos posteriores
        # Por seguridad, mejor no permitir eliminar operaciones
        raise HTTPException(
            status_code=400, 
            detail="No se permite eliminar operaciones de caja. Use un ajuste para corregir errores."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar operación: {str(e)}")
