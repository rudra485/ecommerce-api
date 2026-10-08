from fastapi import FastAPI, Depends
from app.db.database import Base, engine
from app.routers import auth, products, cart, order

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce API")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "ok"}

from app.core.security import get_current_user

@app.get("/protected-test")
def protected_test(current_user = Depends(get_current_user)):
    return {"message": f"Hello, user {current_user.email}!"}

app.include_router(products.router)
app.include_router(cart.router)
app.include_router(order.router)