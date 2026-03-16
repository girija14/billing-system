from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, SessionLocal, engine
from app.models import ShopDenomination
from app.routes import billing, history, products

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billing System")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register route modules
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(billing.router, prefix="/billing", tags=["Billing"])
app.include_router(history.router, prefix="/history", tags=["History"])

# Default denomination values the shop works with
DENOMINATION_VALUES = [500, 50, 20, 10, 5, 2, 1]


@app.on_event("startup")
def startup_event():
    """Ensure default denominations exist in the database on app startup."""
    db = SessionLocal()
    try:
        for val in DENOMINATION_VALUES:
            existing = (
                db.query(ShopDenomination)
                .filter(ShopDenomination.value == val)
                .first()
            )
            if not existing:
                db.add(ShopDenomination(value=val, count=0))
        db.commit()
    finally:
        db.close()


@app.get("/")
async def root():
    """Redirect root URL to the billing page."""
    return RedirectResponse(url="/billing/")
