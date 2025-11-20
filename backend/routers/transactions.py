from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.schemas import Transaction, TransactionCreate
from database import supabase
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=List[Transaction])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    cliente: Optional[str] = None,
    grupo: Optional[str] = None,
    caja_id: Optional[int] = None,
    pagado: Optional[str] = None
):
    """Obtener transacciones con filtros opcionales"""
    try:
        query = supabase.table("transactions").select("*")
        
        # Aplicar filtros
        if fecha_desde:
            query = query.gte("fecha", fecha_desde)
        if fecha_hasta:
            query = query.lte("fecha", fecha_hasta)
        if cliente:
            query = query.ilike("cliente", f"%{cliente}%")
        if grupo:
            query = query.eq("grupo", grupo)
        if caja_id:
            query = query.eq("caja_id", caja_id)
        if pagado:
            query = query.eq("pagado", pagado)
        
        response = query.order("fecha", desc=True).range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones: {str(e)}")

@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: int):
    """Obtener una transacción por ID"""
    try:
        response = supabase.table("transactions").select("*").eq("id", transaction_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacción: {str(e)}")

@router.post("/", response_model=Transaction, status_code=201)
async def create_transaction(transaction: TransactionCreate):
    """Crear una nueva transacción"""
    try:
        transaction_dict = transaction.model_dump()
        print(f"[DEBUG] Transaction data received: {transaction_dict}")
        
        # Registrar en transacciones
        response = supabase.table("transactions").insert(transaction_dict).execute()
        print(f"[DEBUG] Supabase response: {response}")
        created_transaction = response.data[0]
        
        # Si no está pagado, registrar como deudor
        if transaction.pagado == "NO":
            debtor_data = {
                "nombre": transaction.cliente,
                "grupo": transaction.grupo,
                "deuda": transaction.total - transaction.pago,
                "caja_id": transaction.caja_id
            }
            
            # Verificar si el deudor ya existe
            existing_query = supabase.table("debtors").select("*").eq("nombre", transaction.cliente).eq("grupo", transaction.grupo)
            if transaction.caja_id:
                existing_query = existing_query.eq("caja_id", transaction.caja_id)
            existing = existing_query.execute()
            
            if existing.data:
                # Actualizar deuda existente
                new_debt = existing.data[0]["deuda"] + debtor_data["deuda"]
                supabase.table("debtors").update({
                    "deuda": new_debt,
                    "ultima_compra": created_transaction["fecha"]
                }).eq("id", existing.data[0]["id"]).execute()
            else:
                # Crear nuevo deudor
                supabase.table("debtors").insert(debtor_data).execute()
        
        # Registrar movimiento en caja solo si hay pago
        if transaction.pago > 0:
            # Obtener saldo actual de la caja específica
            balance_query = supabase.table("cash_operations").select("*").order("fecha", desc=True).order("id", desc=True).limit(1)
            if transaction.caja_id:
                balance_query = balance_query.eq("caja_id", transaction.caja_id)
            last_operation = balance_query.execute()
            
            # Si no hay operaciones previas, obtener saldo inicial de la caja
            if not last_operation.data and transaction.caja_id:
                caja = supabase.table("cajas").select("saldo_inicial").eq("id", transaction.caja_id).execute()
                current_balance = caja.data[0]["saldo_inicial"] if caja.data else 0
            else:
                current_balance = last_operation.data[0]["saldo"] if last_operation.data else 0
            
            # Usar el TOTAL de la venta, no el pago
            cash_operation = {
                "tipo_operacion": "VENTA",
                "monto": transaction.total,  # Total de la venta, no el pago
                "descripcion": f"Venta a {transaction.cliente} - {len(transaction.productos)} productos",
                "caja_id": transaction.caja_id,
                "saldo": current_balance + transaction.total  # Sumar el total
            }
            
            supabase.table("cash_operations").insert(cash_operation).execute()
        
        return created_transaction
    except Exception as e:
        print(f"[ERROR] Error creating transaction: {str(e)}")
        print(f"[ERROR] Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al crear transacción: {str(e)}")

@router.get("/stats/daily")
async def get_daily_stats(fecha: Optional[str] = None):
    """Obtener estadísticas del día"""
    try:
        if not fecha:
            fecha = datetime.now().strftime("%Y-%m-%d")
        
        fecha_inicio = f"{fecha}T00:00:00"
        fecha_fin = f"{fecha}T23:59:59"
        
        # Transacciones del día
        transactions = supabase.table("transactions").select("*").gte("fecha", fecha_inicio).lte("fecha", fecha_fin).execute()
        
        total_ventas = sum(t["total"] for t in transactions.data)
        total_efectivo = sum(t["pago"] for t in transactions.data)
        total_credito = sum(t["total"] - t["pago"] for t in transactions.data if t["pagado"] == "NO")
        
        return {
            "fecha": fecha,
            "total_transacciones": len(transactions.data),
            "total_ventas": total_ventas,
            "total_efectivo": total_efectivo,
            "total_credito": total_credito,
            "promedio_ticket": total_ventas / len(transactions.data) if transactions.data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.get("/stats/monthly")
async def get_monthly_stats(year: int = Query(...), month: int = Query(..., ge=1, le=12)):
    """Obtener estadísticas del mes"""
    try:
        fecha_inicio = f"{year}-{month:02d}-01T00:00:00"
        
        # Calcular último día del mes
        if month == 12:
            next_month = f"{year + 1}-01-01"
        else:
            next_month = f"{year}-{month + 1:02d}-01"
        
        transactions = supabase.table("transactions").select("*").gte("fecha", fecha_inicio).lt("fecha", next_month).execute()
        
        total_ventas = sum(t["total"] for t in transactions.data)
        total_efectivo = sum(t["pago"] for t in transactions.data)
        
        return {
            "year": year,
            "month": month,
            "total_transacciones": len(transactions.data),
            "total_ventas": total_ventas,
            "total_efectivo": total_efectivo,
            "promedio_diario": total_ventas / 30 if transactions.data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas mensuales: {str(e)}")

@router.get("/by-teacher/{teacher_name}", response_model=List[Transaction])
async def get_transactions_by_teacher(
    teacher_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    only_unpaid: bool = False
):
    """Obtener todas las transacciones de un maestro específico"""
    try:
        query = supabase.table("transactions").select("*").eq("cliente", teacher_name)
        
        # Aplicar filtros
        if fecha_desde:
            query = query.gte("fecha", fecha_desde)
        if fecha_hasta:
            query = query.lte("fecha", fecha_hasta)
        if only_unpaid:
            query = query.eq("pagado", "NO")
        
        response = query.order("fecha", desc=True).range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones del maestro: {str(e)}")

@router.get("/by-teacher/{teacher_name}/summary")
async def get_teacher_summary(teacher_name: str):
    """Obtener resumen de transacciones de un maestro"""
    try:
        # Obtener todas las transacciones del maestro
        transactions = supabase.table("transactions").select("*").eq("cliente", teacher_name).execute()
        
        if not transactions.data:
            return {
                "teacher_name": teacher_name,
                "total_transactions": 0,
                "total_amount": 0,
                "total_paid": 0,
                "total_pending": 0,
                "unpaid_transactions": []
            }
        
        total_amount = sum(t["total"] for t in transactions.data)
        total_paid = sum(t["pago"] for t in transactions.data)
        total_pending = sum(t["total"] - t["pago"] for t in transactions.data if t["pagado"] == "NO")
        unpaid_transactions = [t for t in transactions.data if t["pagado"] == "NO"]
        
        return {
            "teacher_name": teacher_name,
            "grupo": transactions.data[0]["grupo"] if transactions.data else "",
            "total_transactions": len(transactions.data),
            "total_amount": total_amount,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "unpaid_transactions": unpaid_transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen del maestro: {str(e)}")
