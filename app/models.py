from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    product_id = Column(String(50), unique=True, nullable=False, index=True)
    available_stocks = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    tax_percentage = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Product {self.product_id}: {self.name}>"


class ShopDenomination(Base):
    __tablename__ = "shop_denominations"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, unique=True, nullable=False)
    count = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Denomination {self.value}: {self.count}>"


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_without_tax = Column(Float, nullable=False)
    total_tax = Column(Float, nullable=False)
    net_price = Column(Float, nullable=False)
    rounded_net_price = Column(Float, nullable=False)
    cash_paid = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)

    items = relationship(
        "PurchaseItem", back_populates="purchase", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Purchase #{self.id} by {self.customer_email}>"


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    product_id = Column(String(50), nullable=False)
    product_name = Column(String(255), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_price = Column(Float, nullable=False)
    tax_percentage = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    purchase = relationship("Purchase", back_populates="items")

    def __repr__(self):
        return f"<PurchaseItem {self.product_id} x{self.quantity}>"
