from app import create_app, db
from app.models import MenuItem

app = create_app()

with app.app_context():
    # temporary pizza items
    MenuItem.query.delete()

    items = [
        MenuItem(
            name="Margherita",
            category="pizza",
            price=12.5,
            description="Tomato, mozzarella, basil"
        ),
        MenuItem(
            name="Pepperoni",
            category="pizza",
            price=14.0,
            description="Pepperoni and cheese"
        ),
        MenuItem(
            name="Coca-Cola",
            category="drink",
            price=2.5,
            description="33cl"
        ),
        MenuItem(
            name="Tiramisu",
            category="dessert",
            price=5.0,
            description="Italian dessert"
        )
    ]

    db.session.bulk_save_objects(items)
    db.session.commit()

