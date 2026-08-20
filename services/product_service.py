from repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self):
        self.product_repository = ProductRepository()

    def create_product(self, name, price, stock):
        if not name or price is None or stock is None:
            raise ValueError("Faltan datos para crear el producto")

        return self.product_repository.create(name, float(price), int(stock))
