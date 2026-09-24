<<<<<<< HEAD
=======
"""Modelo de datos de un producto del catalogo (FakeStore API)."""

>>>>>>> julio
from __future__ import annotations

from dataclasses import dataclass, field

<<<<<<< HEAD

@dataclass
class Rating:
    rate: float = 0.0
    count: int = 0


@dataclass
class Product:
    id: int = 0
    title: str = ""
    price: float = 0.0
    description: str = ""
    category: str = ""
    image: str = ""
    rating: Rating = field(default_factory=Rating)

    @classmethod
    def from_dict(cls, data: dict) -> Product:
        rating_data = data.get("rating", {})
        return cls(
            id=data.get("id", 0),
            title=data.get("title", ""),
            price=float(data.get("price", 0.0)),
            description=data.get("description", ""),
            category=data.get("category", ""),
            image=data.get("image", ""),
            rating=Rating(
                rate=float(rating_data.get("rate", 0.0)),
                count=int(rating_data.get("count", 0)),
            ),
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "category": self.category,
            "image": self.image,
        }
=======
# Traduccion de las categorias que devuelve la API al espanol.
CATEGORIAS_LEGIBLES = {
    "electronics": "Electronica",
    "jewelery": "Joyería",
    "men's clothing": "Ropa de caballero",
    "women's clothing": "Ropa de dama",
}


@dataclass
class Calificacion:
    """Valoracion media y numero de votos que trae cada producto."""

    tasa: float = 0.0
    conteo: int = 0


@dataclass
class Producto:
    """Producto del catalogo con los campos mas importantes de la API."""

    id: int = 0
    titulo: str = ""
    precio: float = 0.0
    descripcion: str = ""
    categoria: str = ""
    imagen: str = ""
    calificacion: Calificacion = field(default_factory=Calificacion)

    @classmethod
    def from_json(cls, datos: dict) -> "Producto":
        """Construye un Producto a partir del JSON que devuelve la API."""
        rate = datos.get("rating", {})
        return cls(
            id=datos.get("id", 0),
            titulo=datos.get("title", ""),
            precio=datos.get("price", 0.0),
            descripcion=datos.get("description", ""),
            categoria=datos.get("category", ""),
            imagen=datos.get("image", ""),
            calificacion=Calificacion(
                tasa=rate.get("rate", 0.0),
                conteo=rate.get("count", 0),
            ),
        )

    def nombre_categoria(self) -> str:
        """Devuelve la categoria traducida (o la original si no hay traduccion)."""
        return CATEGORIAS_LEGIBLES.get(self.categoria, self.categoria)

    def precio_formateado(self) -> str:
        """Precio con formato monetario: $123.45."""
        return f"${self.precio:,.2f}"
>>>>>>> julio
