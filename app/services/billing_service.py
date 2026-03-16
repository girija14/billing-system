import math

from sqlalchemy.orm import Session

from app.models import Product, Purchase, PurchaseItem, ShopDenomination
from app.services.denomination_service import calculate_balance_denominations


def process_bill(
    db: Session,
    customer_email: str,
    items: list[dict],
    cash_paid: float,
    denom_counts: dict,
) -> dict:
    """
    Validate inputs, compute bill totals, calculate balance denominations,
    persist purchase records, and return the full bill result.

    Returns a dict with either an "error" key or the complete bill data.
    """
    # --- Input validation ---
    if not customer_email:
        return {"error": "Customer email is required."}

    if not items:
        return {"error": "At least one product is required."}

    # --- Build line items ---
    bill_items = []
    total_without_tax = 0.0
    total_tax = 0.0

    for item in items:
        product = (
            db.query(Product)
            .filter(Product.product_id == item["product_id"])
            .first()
        )
        if not product:
            return {"error": f"Product '{item['product_id']}' not found."}

        if product.available_stocks < item["quantity"]:
            return {
                "error": (
                    f"Insufficient stock for '{product.name}' "
                    f"(ID: {product.product_id}). "
                    f"Available: {product.available_stocks}, "
                    f"Requested: {item['quantity']}"
                )
            }

        quantity = item["quantity"]
        unit_price = product.price
        purchase_price = round(unit_price * quantity, 2)
        tax_amount = round(purchase_price * product.tax_percentage / 100, 2)
        total_price = round(purchase_price + tax_amount, 2)

        bill_items.append(
            {
                "product_id": product.product_id,
                "product_name": product.name,
                "unit_price": unit_price,
                "quantity": quantity,
                "purchase_price": purchase_price,
                "tax_percentage": product.tax_percentage,
                "tax_amount": tax_amount,
                "total_price": total_price,
            }
        )

        total_without_tax += purchase_price
        total_tax += tax_amount

    # --- Totals ---
    total_without_tax = round(total_without_tax, 2)
    total_tax = round(total_tax, 2)
    net_price = round(total_without_tax + total_tax, 2)
    rounded_net_price = math.floor(net_price)

    if cash_paid < rounded_net_price:
        return {
            "error": (
                f"Insufficient payment. Bill total is {rounded_net_price:.2f}, "
                f"but cash paid is {cash_paid:.2f}."
            )
        }

    balance = cash_paid - rounded_net_price

    # --- Balance denomination calculation ---
    balance_denoms, remaining = calculate_balance_denominations(balance, denom_counts)

    if remaining > 0:
        return {
            "error": (
                f"Cannot provide exact change. Short by {remaining}. "
                "Please update shop denominations."
            )
        }

    # --- Persist: deduct product stock ---
    for item in items:
        product = (
            db.query(Product)
            .filter(Product.product_id == item["product_id"])
            .first()
        )
        product.available_stocks -= item["quantity"]

    # --- Persist: deduct used denominations from shop ---
    for val, count in balance_denoms:
        denom = (
            db.query(ShopDenomination)
            .filter(ShopDenomination.value == val)
            .first()
        )
        if denom:
            denom.count -= count

    # --- Persist: create purchase record ---
    purchase = Purchase(
        customer_email=customer_email,
        total_without_tax=total_without_tax,
        total_tax=total_tax,
        net_price=net_price,
        rounded_net_price=float(rounded_net_price),
        cash_paid=cash_paid,
        balance=balance,
    )
    db.add(purchase)
    db.flush()  # get purchase.id

    for bi in bill_items:
        db.add(
            PurchaseItem(
                purchase_id=purchase.id,
                product_id=bi["product_id"],
                product_name=bi["product_name"],
                unit_price=bi["unit_price"],
                quantity=bi["quantity"],
                purchase_price=bi["purchase_price"],
                tax_percentage=bi["tax_percentage"],
                tax_amount=bi["tax_amount"],
                total_price=bi["total_price"],
            )
        )

    db.commit()

    return {
        "customer_email": customer_email,
        "items": bill_items,
        "total_without_tax": total_without_tax,
        "total_tax": total_tax,
        "net_price": net_price,
        "rounded_net_price": float(rounded_net_price),
        "cash_paid": cash_paid,
        "balance": balance,
        "balance_denominations": balance_denoms,
    }
