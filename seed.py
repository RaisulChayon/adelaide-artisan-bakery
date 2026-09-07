from decimal import Decimal

from app.database import Base, SessionLocal, engine
from app.models import Product


Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    if db.query(Product).count() == 0:
        products = [
            Product(
                name="Sourdough Loaf",
                category="Bread",
                description="Naturally fermented sourdough with a crisp crust and soft centre.",
                price=Decimal("6.50"),
                available=True,
            ),
            Product(
                name="Almond Croissant",
                category="Pastry",
                description="Buttery croissant filled with almond cream and toasted almonds.",
                price=Decimal("5.50"),
                available=True,
            ),
            Product(
                name="Cinnamon Scroll",
                category="Pastry",
                description="Soft cinnamon pastry finished with a light sweet glaze.",
                price=Decimal("4.50"),
                available=True,
            ),
            Product(
                name="Chocolate Celebration Cake",
                category="Cake",
                description="Rich chocolate cake made for birthdays and special occasions.",
                price=Decimal("32.00"),
                available=True,
            ),
            Product(
                name="Spinach and Feta Roll",
                category="Savoury",
                description="Flaky pastry filled with spinach, feta and herbs.",
                price=Decimal("6.00"),
                available=True,
            ),
        ]

        db.add_all(products)
        db.commit()

        print("Sample products added successfully.")

    else:
        print("Products already exist. No sample data was added.")

finally:
    db.close()