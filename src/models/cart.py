"""Modelo y gestor simple de carrito de compras en memoria."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ItemCarrito:
    producto_id: int
    titulo: str
    precio: float
    imagen: str
    cantidad: int = 1


class Carrito:
    _instancia = None

    def __new__(cls) -> "Carrito":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._items: dict[int, ItemCarrito] = {}
        return cls._instancia

    def agregar(self, producto) -> None:
        if producto.id in self._items:
            self._items[producto.id].cantidad += 1
        else:
            self._items[producto.id] = ItemCarrito(
                producto_id=producto.id,
                titulo=producto.titulo,
                precio=producto.precio,
                imagen=producto.imagen,
                cantidad=1,
            )

    def eliminar(self, producto_id: int) -> None:
        if producto_id in self._items:
            del self._items[producto_id]

    def disminuir(self, producto_id: int) -> None:
        if producto_id in self._items:
            self._items[producto_id].cantidad -= 1
            if self._items[producto_id].cantidad <= 0:
                del self._items[producto_id]

    def vaciar(self) -> None:
        self._items.clear()

    def items(self) -> list[ItemCarrito]:
        return list(self._items.values())

    def total(self) -> float:
        return sum(item.precio * item.cantidad for item in self._items.values())

    def cantidad_total(self) -> int:
        return sum(item.cantidad for item in self._items.values())
