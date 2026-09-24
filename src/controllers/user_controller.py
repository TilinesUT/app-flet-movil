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
    Role.DESCONOCIDO: {
        "titulo": "Sin permisos",
        "icono": "HELP",
        "detalle": "No se pudo determinar un rol valido para este usuario.",
    },
}


class UserController:
    """Singleton con utilidades de presentacion del usuario."""

    _instance: "UserController | None" = None

    def __new__(cls) -> "UserController":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_role_label(self, role: Role) -> str:
        """Nombre legible del rol en espanol."""
        etiquetas = {
            Role.ADMIN: "Administrador",
            Role.AUDITOR: "Auditor",
            Role.CLIENT: "Usuario",
            Role.DESCONOCIDO: "Desconocido",
        }
        return etiquetas.get(role, "Desconocido")

    def get_role_color(self, role: Role) -> str:
        """Color del rol segun la paleta naranja de la app."""
        colores = {
            Role.ADMIN: config.NARANJA,       # administrador -> naranja
            Role.AUDITOR: config.AMARILLO,    # auditor      -> amarillo
            Role.CLIENT: config.NARANJA_SUAVE,  # usuario   -> naranja suave
            Role.DESCONOCIDO: config.TEXTO_ATENUADO,
        }
        return colores.get(role, config.TEXTO_ATENUADO)

    def get_permissions(self, role: Role) -> dict:
        """Informacion de permisos (titulo, icono, detalle) del rol."""
        return _PERMISOS_POR_ROL.get(role, _PERMISOS_POR_ROL[Role.DESCONOCIDO])

    def get_full_name(self, user: UserDTO) -> str:
        """Nombre y apellido del usuario."""
        return f"{user.name.firstname} {user.name.lastname}"

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