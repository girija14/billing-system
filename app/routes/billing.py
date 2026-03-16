from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ShopDenomination
from app.services.billing_service import process_bill
from app.services.email_service import send_invoice_email

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

DENOMINATION_VALUES = [500, 50, 20, 10, 5, 2, 1]


@router.get("/", response_class=HTMLResponse)
async def billing_page(request: Request, db: Session = Depends(get_db)):
    """Display the billing form (Page 1)."""
    denominations = (
        db.query(ShopDenomination)
        .order_by(ShopDenomination.value.desc())
        .all()
    )
    return templates.TemplateResponse(
        "billing/page1.html", {"request": request, "denominations": denominations}
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_bill(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Process the billing form and display the bill (Page 2)."""
    form_data = await request.form()

    customer_email = form_data.get("customer_email", "").strip()

    try:
        cash_paid = float(form_data.get("cash_paid", 0))
    except (ValueError, TypeError):
        cash_paid = 0.0

    # Parse dynamically-added product rows (indices are sequential after JS reindex)
    items = []
    i = 0
    while True:
        pid = form_data.get(f"product_id_{i}")
        if pid is None:
            break
        qty_str = form_data.get(f"quantity_{i}", "")
        pid = pid.strip()
        if pid and qty_str:
            try:
                qty = int(qty_str)
                if qty > 0:
                    items.append({"product_id": pid, "quantity": qty})
            except ValueError:
                pass
        i += 1

    # Parse denomination counts from the form
    denom_counts = {}
    for val in DENOMINATION_VALUES:
        count_str = form_data.get(f"denom_{val}", "0")
        try:
            denom_counts[val] = max(0, int(count_str))
        except (ValueError, TypeError):
            denom_counts[val] = 0

    # Update shop denomination counts in DB (shopkeeper can adjust on each bill)
    for val, count in denom_counts.items():
        denom = (
            db.query(ShopDenomination)
            .filter(ShopDenomination.value == val)
            .first()
        )
        if denom:
            denom.count = count
        else:
            db.add(ShopDenomination(value=val, count=count))
    db.commit()

    # Process the bill (validate, calculate, persist)
    result = process_bill(db, customer_email, items, cash_paid, denom_counts)

    if "error" in result:
        denominations = (
            db.query(ShopDenomination)
            .order_by(ShopDenomination.value.desc())
            .all()
        )
        return templates.TemplateResponse(
            "billing/page1.html",
            {
                "request": request,
                "denominations": denominations,
                "error": result["error"],
            },
        )

    # Send invoice email in the background (non-blocking)
    background_tasks.add_task(send_invoice_email, result)

    return templates.TemplateResponse(
        "billing/page2.html", {"request": request, "result": result}
    )
