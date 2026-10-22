class ShopError(Exception):
    pass

class ProductNotFoundError(ShopError):
    pass

class OutOfStockError(ShopError):
    pass

class InvalidPromoError(ShopError):
    pass

class EmptyCartError(ShopError):
    pass

class OrderNotFoundError(ShopError):
    pass

class InvalidQuantityError(ShopError):
    pass