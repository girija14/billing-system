from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Purchase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def history_search(request: Request):
    """Display the purchase history search form."""
    return templates.TemplateResponse("history/search.html", {"request": request})


@router.get("/purchases", response_class=HTMLResponse)
async def list_purchases(
    request: Request,
    email: str = Query(...),
    db: Session = Depends(get_db),
):
    """List all purchases for a given customer email."""
    purchases = (
        db.query(Purchase)
        .filter(Purchase.customer_email == email)
        .order_by(Purchase.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "history/purchases.html",
        {"request": request, "purchases": purchases, "email": email},
    )


@router.get("/purchases/{purchase_id}", response_class=HTMLResponse)
async def purchase_detail(
    request: Request,
    purchase_id: int,
    db: Session = Depends(get_db),
):
    """Show full details of a single purchase."""
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        return HTMLResponse(content="Purchase not found", status_code=404)
    return templates.TemplateResponse(
        "history/detail.html", {"request": request, "purchase": purchase}
    )
