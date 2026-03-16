from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_products(request: Request, db: Session = Depends(get_db)):
    """Display all products."""
    products = db.query(Product).order_by(Product.product_id).all()
    return templates.TemplateResponse(
        "products/list.html", {"request": request, "products": products}
    )


@router.get("/add", response_class=HTMLResponse)
async def add_product_form(request: Request):
    """Show the form to add a new product."""
    return templates.TemplateResponse(
        "products/form.html", {"request": request, "product": None}
    )


@router.post("/add")
async def add_product(
    request: Request,
    name: str = Form(...),
    product_id: str = Form(...),
    available_stocks: int = Form(...),
    price: float = Form(...),
    tax_percentage: float = Form(...),
    db: Session = Depends(get_db),
):
    """Create a new product."""
    existing = db.query(Product).filter(Product.product_id == product_id).first()
    if existing:
        return templates.TemplateResponse(
            "products/form.html",
            {
                "request": request,
                "product": None,
                "error": f"Product ID '{product_id}' already exists.",
            },
        )

    product = Product(
        name=name,
        product_id=product_id,
        available_stocks=available_stocks,
        price=price,
        tax_percentage=tax_percentage,
    )
    db.add(product)
    db.commit()
    return RedirectResponse(url="/products/", status_code=303)


@router.get("/edit/{id}", response_class=HTMLResponse)
async def edit_product_form(request: Request, id: int, db: Session = Depends(get_db)):
    """Show the form to edit an existing product."""
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        return RedirectResponse(url="/products/")
    return templates.TemplateResponse(
        "products/form.html", {"request": request, "product": product}
    )


@router.post("/edit/{id}")
async def edit_product(
    request: Request,
    id: int,
    name: str = Form(...),
    product_id: str = Form(...),
    available_stocks: int = Form(...),
    price: float = Form(...),
    tax_percentage: float = Form(...),
    db: Session = Depends(get_db),
):
    """Update an existing product."""
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        return RedirectResponse(url="/products/", status_code=303)

    # Ensure product_id uniqueness (excluding self)
    existing = (
        db.query(Product)
        .filter(Product.product_id == product_id, Product.id != id)
        .first()
    )
    if existing:
        return templates.TemplateResponse(
            "products/form.html",
            {
                "request": request,
                "product": product,
                "error": f"Product ID '{product_id}' is already in use.",
            },
        )

    product.name = name
    product.product_id = product_id
    product.available_stocks = available_stocks
    product.price = price
    product.tax_percentage = tax_percentage
    db.commit()
    return RedirectResponse(url="/products/", status_code=303)


@router.post("/delete/{id}")
async def delete_product(id: int, db: Session = Depends(get_db)):
    """Delete a product."""
    product = db.query(Product).filter(Product.id == id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/products/", status_code=303)
