import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.products import Product
from app.schemas.order import CheckoutResponse
from app.core.security import get_current_user, STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0.0
    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")
        total += product.price * item.quantity

    order = Order(user_id=current_user.id, total_amount=total, status="pending")
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {item.product_id} no longer exists")
    db.add(OrderItem(
        order_id=order.id,
        product_id=item.product_id,
        quantity=item.quantity,
        price_at_purchase=product.price,
    ))
    db.commit()

    intent = stripe.PaymentIntent.create(
        amount=int(total * 100),   # Stripe expects the smallest currency unit (cents)
        currency="usd",
        metadata={"order_id": str(order.id)},
    )
    order.stripe_payment_intent_id = intent.id
    db.commit()

    return {"order": order, "client_secret": intent.client_secret}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    event = stripe.Event.construct_from(
        __import__("json").loads(payload), stripe.api_key
    )

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order = db.query(Order).filter(
            Order.stripe_payment_intent_id == intent["id"]
        ).first()
        if order:
            order.status = "paid"
            for item in db.query(OrderItem).filter(OrderItem.order_id == order.id):
                product = db.query(Product).filter(Product.id == item.product_id).first()
                product.stock_quantity -= item.quantity
            cart = db.query(Cart).filter(Cart.user_id == order.user_id).first()
            if cart:
                for cart_item in list(cart.items):
                    db.delete(cart_item)
            db.commit()

    return {"status": "ok"}