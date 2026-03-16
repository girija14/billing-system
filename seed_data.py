"""
Seed the database with sample products and default shop denominations.

Usage:
    python seed_data.py
"""

from app.database import Base, SessionLocal, engine
from app.models import Product, ShopDenomination

# Ensure tables are created
Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        # --- Seed Products ---
        products = [
            Product(
                name="Laptop",
                product_id="P001",
                available_stocks=50,
                price=999.99,
                tax_percentage=12.0,
            ),
            Product(
                name="Wireless Mouse",
                product_id="P002",
                available_stocks=200,
                price=25.50,
                tax_percentage=5.0,
            ),
            Product(
                name="Mechanical Keyboard",
                product_id="P003",
                available_stocks=150,
                price=75.00,
                tax_percentage=5.0,
            ),
            Product(
                name="LED Monitor",
                product_id="P004",
                available_stocks=30,
                price=450.00,
                tax_percentage=18.0,
            ),
            Product(
                name="USB-C Cable",
                product_id="P005",
                available_stocks=500,
                price=10.00,
                tax_percentage=5.0,
            ),
            Product(
                name="Headphones",
                product_id="P006",
                available_stocks=100,
                price=150.00,
                tax_percentage=12.0,
            ),
            Product(
                name="Webcam HD",
                product_id="P007",
                available_stocks=80,
                price=85.00,
                tax_percentage=18.0,
            ),
            Product(
                name="Mouse Pad",
                product_id="P008",
                available_stocks=300,
                price=15.00,
                tax_percentage=5.0,
            ),
        ]

        for p in products:
            existing = (
                db.query(Product).filter(Product.product_id == p.product_id).first()
            )
            if not existing:
                db.add(p)
                print(f"  Added product: {p.product_id} – {p.name}")
            else:
                print(f"  Skipped (exists): {p.product_id} – {p.name}")

        # --- Seed Shop Denominations ---
        default_counts = {500: 10, 50: 20, 20: 30, 10: 50, 5: 50, 2: 100, 1: 100}

        for value, count in sorted(default_counts.items(), reverse=True):
            existing = (
                db.query(ShopDenomination)
                .filter(ShopDenomination.value == value)
                .first()
            )
            if not existing:
                db.add(ShopDenomination(value=value, count=count))
                print(f"  Added denomination: {value} x {count}")
            else:
                print(f"  Skipped (exists): denomination {value}")

        db.commit()
        print("\nDatabase seeded successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
