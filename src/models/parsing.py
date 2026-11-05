"""Utilidades defensivas para mapear respuestas JSON a modelos.

La API puede devolver campos nulos, ausentes o con tipos inesperados
(por ejemplo, un objeto anidado en null). Estas funciones evitan
excepciones al construir los DTO de la aplicacion.
"""

from __future__ import annotations

from typing import Any


def como_dict(valor: Any) -> dict:
    """Devuelve el valor solo si es un diccionario; si no, un dict vacio."""
    return valor if isinstance(valor, dict) else {}


def como_lista(valor: Any) -> list:
    """Devuelve el valor solo si es una lista; si no, una lista vacia."""
    return valor if isinstance(valor, list) else []


def texto(valor: Any) -> str:
    """Convierte un valor a texto seguro (None se transforma en '')."""
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor
    return str(valor)


def entero(valor: Any, defecto: int = 0) -> int:
    """Convierte un valor a entero; ante cualquier fallo usa el defecto."""
    if isinstance(valor, bool):
        return int(valor)
    try:
        return int(valor)
    except (TypeError, ValueError):
        return defecto
