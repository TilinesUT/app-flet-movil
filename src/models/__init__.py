"""Modelo de dominio: roles de los usuarios de la aplicacion.

El rol llega desde la API en el campo `role` de cada usuario:
- ADMIN   -> administrador
- AUDITOR -> auditor
- CLIENT  -> usuario/cliente
"""

from enum import Enum


class Role(Enum):
    """Roles posibles segun el rol que devuelve la API."""

    ADMIN = "admin"
    AUDITOR = "auditor"
    CLIENT = "cliente"
    DESCONOCIDO = "desconocido"

    @staticmethod
    def from_nombre(rol: str | None) -> "Role":
        """Convierte el texto del rol de la API en su enumerado."""
        roles = {
            "ADMIN": Role.ADMIN,
            "AUDITOR": Role.AUDITOR,
            "CLIENT": Role.CLIENT,
        }
        return roles.get((rol or "").strip().upper(), Role.DESCONOCIDO)
