"""Modelo de dominio: roles de los usuarios de la aplicacion.

Reglas de la aplicacion:
- Codigos 1 y 2  -> Administrador
- Codigo 3       -> Auditor
- Codigo 4 o mas -> Usuario/cliente
- Cualquier otro (0 o negativo) -> Desconocido
"""

from enum import Enum


class Role(Enum):
    """Roles posibles segun el codigo (id) del usuario."""

    ADMIN = "admin"
    AUDITOR = "auditor"
    CLIENT = "cliente"
    DESCONOCIDO = "desconocido"

    @staticmethod
    def from_id(user_id: int) -> "Role":
        """Devuelve el rol correspondiente al codigo de usuario."""
        if user_id in (1, 2):            # codigos 1 y 2 -> administrador
            return Role.ADMIN
        if user_id == 3:                 # codigo 3 -> auditor
            return Role.AUDITOR
        if user_id >= 4:                 # codigo 4 o superior -> usuario
            return Role.CLIENT
        return Role.DESCONOCIDO          # 0 o negativo -> desconocido