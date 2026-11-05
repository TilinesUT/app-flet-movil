"""Controlador de usuario (singleton).

Provee utilidades de presentacion sobre el usuario: etiqueta y color del
rol, nombre completo, direccion y los permisos asociados a cada rol.
"""

from __future__ import annotations

import src.config as config
from src.models import Role
from src.models.product import Producto
from src.models.user import UserDTO

# Permisos que se muestran en la tarjeta de perfil segun el rol.
_PERMISOS_POR_ROL = {
    Role.ADMIN: {
        "titulo": "Acceso total",
        "icono": "MANAGE_SEARCH",
        "detalle": "Puede gestionar inventario, ventas, configuracion, usuarios, informes y estadisticas.",
    },
    Role.AUDITOR: {
        "titulo": "Solo lectura",
        "icono": "SEARCH",
        "detalle": "Puede consultar informes y auditar el sistema, sin permisos de escritura.",
    },
    Role.CLIENT: {
        "titulo": "Acceso basico",
        "icono": "VIEW_LIST",
        "detalle": "Puede ver el catalogo, consultar su perfil y comprar productos.",
    },
}


class UserController:
    """Singleton con utilidades de presentacion del usuario."""

    _instance: "UserController | None" = None

    def __new__(cls) -> "UserController":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_role_label(self, role: Role, rol_api: str = "") -> str:
        """Nombre legible del rol en espanol.

        Si el rol no es uno de los conocidos por la app, se muestra el
        nombre tal cual viene de la API.
        """
        etiquetas = {
            Role.ADMIN: "Administrador",
            Role.AUDITOR: "Auditor",
            Role.CLIENT: "Usuario",
        }
        if role in etiquetas:
            return etiquetas[role]
        return (rol_api or "").strip().upper() or "Sin rol"

    def get_role_color(self, role: Role) -> str:
        """Color del rol segun la paleta naranja de la app."""
        colores = {
            Role.ADMIN: config.NARANJA,       # administrador -> naranja
            Role.AUDITOR: config.AMARILLO,    # auditor      -> amarillo
            Role.CLIENT: config.NARANJA_SUAVE,  # usuario   -> naranja suave
            Role.DESCONOCIDO: config.TEXTO_ATENUADO,
        }
        return colores.get(role, config.TEXTO_ATENUADO)

    def get_permissions(self, role: Role, rol_api: str = "") -> dict:
        """Informacion de permisos (titulo, icono, detalle) del rol."""
        if role in _PERMISOS_POR_ROL and role is not Role.DESCONOCIDO:
            return _PERMISOS_POR_ROL[role]

        return {
            "titulo": self.get_role_label(role, rol_api),
            "icono": "HELP",
            "detalle": "La API no define permisos especificos para este rol.",
        }

    def get_full_name(self, user: UserDTO) -> str:
        """Nombre y apellido del usuario."""
        return user.nombre_completo()

    def get_full_address(self, user: UserDTO) -> str:
        """Direccion completa formateada del usuario."""
        return (
            f"{user.address.street} {user.address.number}, "
            f"{user.address.city} ({user.address.zipcode})"
        )

    def get_price(self, producto: Producto) -> str:
        """Precio del producto con formato monetario."""
        return producto.precio_formateado()

    def get_category(self, producto: Producto) -> str:
        """Categoria del producto traducida al espanol."""
        return producto.nombre_categoria()