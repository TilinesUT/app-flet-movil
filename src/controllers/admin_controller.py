"""Controlador de administrador (singleton).

Contiene la logica de negocio exclusiva de los administradores:
- Verificacion del rol de administrador (solo codigos 1 y 2).
- Lista de permisos tipicos de un administrador.
- Gestion (CRUD) de los articulos del catalogo.
- Estadisticas simples del catalogo para el panel.
"""

from __future__ import annotations

from src.models import Role
from src.models.product import Producto
from src.models.session import Session
from src.models.user import UserDTO
from src.services.api_service import ApiService

# Permisos tipicos de un administrador, mostrados en su panel.
_PERMISOS_ADMIN = [
    {
        "icono": "INVENTORY",
        "titulo": "Gestion de articulos",
        "detalle": "Crear, editar y eliminar productos del catalogo.",
        "funcional": True,
    },
    {
        "icono": "GROUPS",
        "titulo": "Gestion de usuarios",
        "detalle": "Moderar cuentas, accesos y datos de los usuarios.",
        "funcional": False,
    },
    {
        "icono": "BAR_CHART",
        "titulo": "Informes y estadisticas",
        "detalle": "Consultar metricas del negocio y del inventario.",
        "funcional": False,
    },
    {
        "icono": "TUNE",
        "titulo": "Configuracion del sistema",
        "detalle": "Ajustar parametros generales de la aplicacion.",
        "funcional": False,
    },
    {
        "icono": "POLICY",
        "titulo": "Roles y permisos",
        "detalle": "Asignar y administrar los roles de la plataforma.",
        "funcional": False,
    },
]


class AdminController:
    """Singleton que concentra las tareas del administrador."""

    _instance: "AdminController | None" = None
    _api: ApiService

    def __new__(cls) -> "AdminController":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api = ApiService()
        return cls._instance

    # ------------------------------------------------------------------
    # Acceso y permisos
    # ------------------------------------------------------------------
    def es_administrador(self, rol: Role | None) -> bool:
        """True solo si el rol es de administrador (codigos 1 y 2)."""
        return rol is Role.ADMIN

    def permisos_administrador(self) -> list[dict]:
        """Lista de capacidades tipicas del rol administrador."""
        return list(_PERMISOS_ADMIN)

    # ------------------------------------------------------------------
    # Gestion de articulos (delega las llamadas a la API)
    # ------------------------------------------------------------------
    def obtener_articulos(self, filtro: str = "") -> list[Producto]:
        """Articulos del catalogo, opcionalmente filtrados por nombre."""
        productos = self._api.obtener_productos()
        if filtro:
            productos = [
                p for p in productos if filtro.lower() in p.titulo.lower()
            ]
        return productos

    def crear_articulo(self, producto: Producto) -> Producto:
        """Da de alta un nuevo articulo en el catalogo."""
        return self._api.crear_producto(producto)

    def actualizar_articulo(self, producto: Producto, id_original: int) -> Producto:
        """Actualiza un articulo existente del catalogo."""
        if id_original != producto.id:
            # El id no se debe cambiar al editar; se preserva el original.
            producto.id = id_original
        return self._api.actualizar_producto(producto)

    def eliminar_articulo(self, producto_id: int) -> None:
        """Elimina un articulo del catalogo por su id."""
        self._api.eliminar_producto(producto_id)

    # ------------------------------------------------------------------
    # Estadisticas para el panel
    # ------------------------------------------------------------------
    def estadisticas(self) -> dict:
        """Resumen numerico del catalogo (total, categorias, precio medio)."""
        productos = self._api.obtener_productos()
        precios = [p.precio for p in productos]
        return {
            "total": len(productos),
            "categorias": len({p.categoria for p in productos}),
            "precio_promedio": (sum(precios) / len(precios)) if precios else 0.0,
        }

    def categorias(self) -> list[str]:
        """Categorias disponibles para el formulario de articulos."""
        return self._api.obtener_categorias()

    # ------------------------------------------------------------------
    # Utilidades de la capa de presentacion
    # ------------------------------------------------------------------
    def precio_texto(self, producto: Producto) -> str:
        """Precio formateado del articulo."""
        return producto.precio_formateado()

    def nombre_categoria(self, categoria: str) -> str:
        """Traduce la categoria al espanol (o la deja igual)."""
        from src.models.product import CATEGORIAS_LEGIBLES

        return CATEGORIAS_LEGIBLES.get(categoria, categoria)

    @staticmethod
    def usuario_actual() -> UserDTO | None:
        """Devuelve el usuario en sesion (para la cabecera del panel)."""
        return Session().user