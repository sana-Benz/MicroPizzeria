from .models import MenuItem


def seed_menu(db):
    if MenuItem.query.count() > 0:
        return

    items = [
        # Pizzas
        MenuItem(
            name="Margherita",
            category="pizza",
            price=12.5,
            description="Tomate, mozzarella fraîche et basilic"
        ),
        MenuItem(
            name="Pepperoni",
            category="pizza",
            price=14.0,
            description="Pepperoni épicé et fromage fondant"
        ),
        MenuItem(
            name="Végétarienne",
            category="pizza",
            price=13.0,
            description="Poivrons grillés, champignons, olives et courgettes"
        ),
        MenuItem(
            name="Fruits de mer",
            category="pizza",
            price=16.5,
            description="Crevettes, calamars, moules et sauce tomate"
        ),
        MenuItem(
            name="Bœuf",
            category="pizza",
            price=15.0,
            description="Bœuf haché, oignons caramélisés et mozzarella"
        ),
        MenuItem(
            name="Poulet",
            category="pizza",
            price=14.5,
            description="Poulet grillé, sauce barbecue et poivrons"
        ),
        MenuItem(
            name="Neptune",
            category="pizza",
            price=15.5,
            description="Thon, olives, câpres et sauce tomate"
        ),

        # Drinks
        MenuItem(
            name="Eau minérale",
            category="drink",
            price=1.5,
            description="Eau minérale naturelle en bouteille 50cl"
        ),
        MenuItem(
            name="Cola",
            category="drink",
            price=2.5,
            description="Boisson gazeuse au cola 33cl"
        ),
        MenuItem(
            name="Sprite",
            category="drink",
            price=2.5,
            description="Boisson gazeuse au citron et à la lime 33cl"
        ),
        MenuItem(
            name="Ice Tea",
            category="drink",
            price=2.5,
            description="Thé glacé à la pêche 33cl"
        ),
        MenuItem(
            name="Eau gazeuse",
            category="drink",
            price=2.0,
            description="Eau pétillante en bouteille 50cl"
        ),

        # Desserts
        MenuItem(
            name="Tiramisu",
            category="dessert",
            price=5.0,
            description="Dessert italien au mascarpone, café et cacao"
        ),
        MenuItem(
            name="Cheesecake",
            category="dessert",
            price=5.5,
            description="Cheesecake new-yorkais au coulis de fruits rouges"
        ),
        MenuItem(
            name="Cannoli",
            category="dessert",
            price=4.5,
            description="Cannoli siciliens à la ricotta et pépites de chocolat"
        ),
        MenuItem(
            name="Panna Cotta",
            category="dessert",
            price=5.0,
            description="Panna cotta à la vanille et coulis de caramel"
        ),
        MenuItem(
            name="Crostata à la confiture",
            category="dessert",
            price=4.5,
            description="Tarte italienne croustillante à la confiture de framboises"
        ),
    ]

    db.session.bulk_save_objects(items)
    db.session.commit()
