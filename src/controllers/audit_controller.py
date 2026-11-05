"""Controlador de auditoria (singleton).

Concentra las consultas de solo lectura para los roles Administrador y
Auditor: directorio de usuarios y historial global de carritos.
"""

from __future__ import annotations

from src.models import Role
from src.models.cart_history import CartDTO
from src.models.user import UserDTO
from src.services.api_service import ApiService


class AuditController:
    """Singleton con las consultas y reglas de acceso de auditoria."""

    _instance: "AuditController | None" = None
    _api: ApiService

    def __new__(cls) -> "AuditController":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api = ApiService()
        return cls._instance

    # ------------------------------------------------------------------
    # Permisos de lectura
    # ------------------------------------------------------------------
    @staticmethod
    def puede_ver_usuarios(rol: Role | None) -> bool:
        """True para administradores y auditores (clientes quedan fuera)."""
        return rol in (Role.ADMIN, Role.AUDITOR)

    @staticmethod
    def puede_ver_carritos(rol: Role | None) -> bool:
        """True para administradores y auditores (clientes quedan fuera)."""
        return rol in (Role.ADMIN, Role.AUDITOR)

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def usuarios(self) -> list[UserDTO]:
        """Directorio completo de cuentas registradas."""
        return self._api.obtener_usuarios()

    def carritos(self) -> list[CartDTO]:
        """Historial global de carritos."""
        return self._api.obtener_carritos()

    def titulos_productos(self) -> dict[int, str]:
        """Mapa id -> titulo para cruzar los articulos de los carritos."""
        return {p.id: p.titulo for p in self._api.obtener_productos()}
