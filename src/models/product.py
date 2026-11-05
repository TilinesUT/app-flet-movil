"""Modelo de datos de un producto del catalogo."""

from __future__ import annotations

from dataclasses import dataclass, field

# Traduccion de las categorias que devuelve la API al espanol.
CATEGORIAS_LEGIBLES = {
    "electronics": "Electronica",
    "jewelery": "Joyería",
    "men's clothing": "Ropa de caballero",
    "women's clothing": "Ropa de dama",
}


def _numero(valor, defecto: float = 0.0) -> float:
    """Convierte un valor a float sin lanzar excepciones."""
    try:
        return float(valor)
    except (TypeError, ValueError):
        return defecto


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
        rating = datos.get("rating")
        if isinstance(rating, dict):
            tasa = rating.get("rate", 0.0)
            conteo = rating.get("count", 0)
        else:
            tasa = datos.get("rating_rate", 0.0)
            conteo = datos.get("rating_count", 0)

        return cls(
            id=int(_numero(datos.get("id"))),
            titulo=str(datos.get("title", "")),
            precio=_numero(datos.get("price")),
            descripcion=str(datos.get("description", "")),
            categoria=str(datos.get("category", "")),
            imagen=str(datos.get("image", "")),
            calificacion=Calificacion(
                tasa=_numero(tasa),
                conteo=int(_numero(conteo)),
            ),
        )

    def nombre_categoria(self) -> str:
        """Devuelve la categoria traducida (o la original si no hay traduccion)."""
        return CATEGORIAS_LEGIBLES.get(self.categoria, self.categoria)

    def precio_formateado(self) -> str:
        """Precio con formato monetario: $123.45."""
        return f"${self.precio:,.2f}"
