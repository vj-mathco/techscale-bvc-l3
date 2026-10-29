# TechScale: HTTP routing layer
# Route handlers receive HTTP input and delegate to service and repository layers.
# No pricing logic, validation rules, or SQL belongs in this file.

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import order_service
import order_repository

router = APIRouter()


class OrderCreate(BaseModel):
    customer_id: str
    product_id: int
    quantity: int


# TODO: Implement two route handlers.
#
# 1. POST /orders: accept an order request, validate the quantity via the service layer,
#    calculate the price via the service layer, and return the total price and status.
#    Surface any validation rejection as a 422 response.
#
# 2. GET /orders/top: fetch the top orders via the repository layer.
#    Return a 404 if no orders exist.
@router.post("/orders")
async def create_order(order: OrderCreate):
    try:
        order_service.validate_order(order.quantity)
        total_price = order_service.calculate_price(order.product_id, order.quantity)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return {"total_price": total_price, "status": "pending"}


@router.get("/orders/top")
async def get_top_orders():
    orders = await run_in_threadpool(order_repository.get_top_orders)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders
