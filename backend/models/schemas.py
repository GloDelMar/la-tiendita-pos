from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Modelos para Cajas
class CajaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    activa: bool = True
    saldo_inicial: float = Field(default=0)

class CajaCreate(CajaBase):
    pass

class CajaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    activa: Optional[bool] = None
    saldo_inicial: Optional[float] = None

class Caja(CajaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = None
    caja_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    caja_id: Optional[int] = None

class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductInTransaction(BaseModel):
    nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float

class TransactionBase(BaseModel):
    cliente: str = "Cliente"
    grupo: str = "General"
    productos: List[ProductInTransaction]
    total: float = Field(..., gt=0)
    pago: float = Field(..., ge=0)
    cambio: float = Field(..., ge=0)
    pagado: str = Field(..., pattern="^(SI|NO)$")
    caja_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True

class DebtorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    grupo: str = Field(..., min_length=1, max_length=200)
    deuda: float = Field(..., gt=0)

class DebtorCreate(DebtorBase):
    pass

class DebtorUpdate(BaseModel):
    deuda: Optional[float] = Field(None, gt=0)

class Debtor(DebtorBase):
    id: int
    fecha_primera_deuda: datetime
    ultima_compra: datetime

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    """Response para pagos de deuda"""
    mensaje: str
    deuda_restante: float
    debtor: Optional[dict] = None  # Opcional, solo si no se eliminó

class CashOperationBase(BaseModel):
    tipo_operacion: str = Field(..., pattern="^(VENTA|INGRESO|EGRESO|AJUSTE)$")
    monto: float = Field(..., ne=0)
    descripcion: Optional[str] = None
    caja_id: Optional[int] = None

class CashOperationCreate(CashOperationBase):
    pass

class CashOperation(CashOperationBase):
    id: int
    saldo: float
    fecha: datetime

    class Config:
        from_attributes = True
