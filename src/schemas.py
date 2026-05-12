from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    size: str
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    new_count: int

class ProductResponse(ProductBase):
    id: int

class DemandResponse(BaseModel):
    chat_id: int
    product_name: str
    size: Optional[str]
    status: str