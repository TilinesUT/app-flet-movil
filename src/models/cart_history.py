"""Modelos del historial global de carritos (FakeStore /carts)."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.models.parsing import como_dict, como_lista, entero, texto


@dataclass
class CartItemDTO:
    """Articulo dentro de un carrito: producto y cantidad."""

    product_id: int = 0
    quantity: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "CartItemDTO":
        datos = como_dict(data)
        product_id = datos.get("productId", datos.get("product_id"))
        return cls(
            product_id=entero(product_id),
            quantity=entero(datos.get("quantity")),
        )


@dataclass
class CartDTO:
    """Carrito global: propietario, fecha y articulos."""

    id: int = 0
    user_id: int = 0
    date: str = ""
    products: list[CartItemDTO] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "CartDTO":
        datos = como_dict(data)
        productos = [
            CartItemDTO.from_dict(item)
            for item in como_lista(datos.get("products"))
            if isinstance(item, dict)
        ]
        return cls(
            id=entero(datos.get("id")),
            user_id=entero(datos.get("userId", datos.get("user_id"))),
            date=texto(datos.get("date")),
            products=productos,
        )

    def cantidad_total(self) -> int:
        """Suma de las cantidades de todos los articulos del carrito."""
        return sum(item.quantity for item in self.products)

    def cantidad_productos(self) -> int:
        """Numero de lineas (productos distintos) del carrito."""
        return len(self.products)
