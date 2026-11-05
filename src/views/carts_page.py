"""Vista del historial global de carritos (US12).

Solo accesible para administradores y auditores. Lista el id del carrito,
la fecha de creacion y el id del propietario; al expandir cada carrito se
muestran los productos (id + cantidad) y, cruzando con /products, su
titulo real. La pantalla es estrictamente de solo lectura.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

import flet as ft

import src.config as config
from src.controllers.audit_controller import AuditController
from src.controllers.auth_controller import AuthController
from src.models.cart_history import CartDTO, CartItemDTO
from src.views.navigation import crear_barra_navegacion
from src.views.widgets import pantalla_acceso_denegado


class CartsPage:
    """Monitor de carritos globales con desglose de articulos."""

    def __init__(
        self,
        page: ft.Page,
        on_home,
        on_catalog,
        on_admin=None,
        on_usuarios=None,
        on_carritos=None,
    ) -> None:
        self._page = page
        self._on_home = on_home
        self._on_catalog = on_catalog
        self._on_admin = on_admin
        self._on_usuarios = on_usuarios
        self._on_carritos = on_carritos
        self._audit = AuditController()
        self._auth = AuthController()
        self._carritos: list[CartDTO] = []
        self._titulos: dict[int, str] = {}
        self._contenido = None
        self._contador = None

    # ------------------------------------------------------------------
    # Construccion de la vista
    # ------------------------------------------------------------------
    def build(self) -> ft.Container:
        """Construye el monitor; sin rol autorizado muestra bloqueo."""
        if not self._audit.puede_ver_carritos(self._auth.current_role):
            return pantalla_acceso_denegado(
                "El historial global de carritos solo esta disponible para "
                "administradores y auditores.",
                self._on_home,
            )

        cabecera = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "CARRITOS",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_ATENUADO,
                        ),
                        ft.Text(
                            "Historial global",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_PRIMARIO,
                        ),
                    ],
                    spacing=0,
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_color=config.NARANJA,
                    tooltip="Recargar carritos",
                    on_click=self._on_cargar,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self._contador = ft.Text(
            "Cargando...",
            size=12,
            color=config.TEXTO_ATENUADO,
        )
        self._contenido = ft.Container(
            expand=True,
            content=self._estado_cargando(),
        )

        navegacion = crear_barra_navegacion(
            self._auth.current_role,
            "carritos",
            self._on_home,
            self._on_catalog,
            self._on_admin,
            self._on_usuarios,
            self._on_carritos,
        )

        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[config.NEGRO, config.CARBON, config.NEGRO],
            ),
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[cabecera, self._contador],
                            spacing=8,
                        ),
                        padding=ft.Padding.all(16),
                    ),
                    self._contenido,
                    navegacion,
                ],
                spacing=0,
                expand=True,
            ),
        )

    # ------------------------------------------------------------------
    # Estados
    # ------------------------------------------------------------------
    def _estado_cargando(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(color=config.NARANJA, stroke_width=4),
                    ft.Text(
                        "Cargando carritos...",
                        size=13,
                        color=config.TEXTO_SECUNDARIO,
                    ),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(top=48),
        )

    def _estado_error(self, mensaje: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.CLOUD_OFF,
                        size=42,
                        color=config.TEXTO_ATENUADO,
                    ),
                    ft.Text(
                        mensaje,
                        size=13,
                        color=config.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.TextButton("Reintentar", on_click=self._on_cargar),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(top=48),
        )

    def _estado_vacio(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.REMOVE_SHOPPING_CART,
                        size=42,
                        color=config.TEXTO_ATENUADO,
                    ),
                    ft.Text(
                        "No hay carritos registrados.",
                        size=13,
                        color=config.TEXTO_SECUNDARIO,
                    ),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(top=48),
        )

    # ------------------------------------------------------------------
    # Carga y pintado
    # ------------------------------------------------------------------
    async def _cargar(self) -> None:
        """Descarga carritos y catalogo, y pinta el historial."""
        if not self._audit.puede_ver_carritos(self._auth.current_role):
            return

        self._contenido.content = self._estado_cargando()
        self._page.update()

        try:
            carritos, titulos = await asyncio.gather(
                asyncio.to_thread(self._audit.carritos),
                asyncio.to_thread(self._audit.titulos_productos),
            )
        except Exception:
            self._contenido.content = self._estado_error(
                "No se pudo cargar el historial de carritos. "
                "Revisa tu conexion e intenta de nuevo."
            )
            self._page.update()
            return

        self._carritos = carritos
        self._titulos = titulos
        self._pintar()

    def _on_cargar(self, e) -> None:
        self._page.run_task(self._cargar)

    def _pintar(self) -> None:
        ordenados = sorted(
            self._carritos,
            key=lambda c: (c.date, c.id),
            reverse=True,
        )
        unidades = sum(c.cantidad_total() for c in ordenados)
        self._contador.value = (
            f"{len(ordenados)} carrito(s) · {unidades} articulo(s)"
        )

        if not ordenados:
            estado = self._estado_vacio()
        else:
            estado = ft.ListView(
                controls=[self._tarjeta_carrito(c) for c in ordenados],
                spacing=8,
                padding=ft.Padding(left=16, right=16, bottom=16),
                expand=True,
            )

        self._contenido.content = estado
        self._page.update()

    # ------------------------------------------------------------------
    # Tarjeta expandible de cada carrito
    # ------------------------------------------------------------------
    @staticmethod
    def _fecha_legible(valor: str) -> str:
        if not valor:
            return "Fecha no disponible"
        try:
            fecha = datetime.fromisoformat(valor.replace("Z", "+00:00"))
            return fecha.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return valor

    def _fila_articulo(self, item: CartItemDTO) -> ft.Row:
        titulo = self._titulos.get(item.product_id)
        if not titulo:
            titulo = f"Producto #{item.product_id}"

        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.INVENTORY_2,
                        size=16,
                        color=config.NARANJA_SUAVE,
                    ),
                    width=32,
                    height=32,
                    alignment=ft.Alignment.CENTER,
                    bgcolor=config.GRAFITO,
                    border_radius=ft.BorderRadius.all(8),
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            titulo,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_PRIMARIO,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            f"Producto #{item.product_id}",
                            size=10,
                            color=config.TEXTO_ATENUADO,
                        ),
                    ],
                    spacing=1,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Text(
                        f"x{item.quantity}",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=config.NARANJA,
                    ),
                    padding=ft.Padding(left=10, top=4, right=10, bottom=4),
                    bgcolor=config.GRAFITO,
                    border_radius=ft.BorderRadius.all(8),
                ),
            ],
            spacing=10,
        )

    def _tarjeta_carrito(self, carrito: CartDTO) -> ft.ExpansionTile:
        if carrito.products:
            detalle: list[ft.Control] = [
                self._fila_articulo(item) for item in carrito.products
            ]
            detalle.append(
                ft.Text(
                    f"{carrito.cantidad_productos()} producto(s) distinto(s) · "
                    f"{carrito.cantidad_total()} unidad(es)",
                    size=10,
                    color=config.TEXTO_ATENUADO,
                )
            )
        else:
            detalle = [
                ft.Text(
                    "Este carrito no tiene articulos registrados.",
                    size=12,
                    color=config.TEXTO_SECUNDARIO,
                )
            ]

        fecha = self._fecha_legible(carrito.date)
        forma = ft.RoundedRectangleBorder(
            radius=12,
            side=ft.BorderSide(width=1, color=config.BORDE),
        )

        return ft.ExpansionTile(
            title=ft.Text(
                f"Carrito #{carrito.id}",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=config.TEXTO_PRIMARIO,
            ),
            subtitle=ft.Text(
                f"Usuario #{carrito.user_id} · {fecha}",
                size=11,
                color=config.TEXTO_SECUNDARIO,
            ),
            leading=ft.Icon(
                ft.Icons.SHOPPING_CART_OUTLINED,
                size=20,
                color=config.NARANJA,
            ),
            controls=[
                ft.Container(
                    content=ft.Column(controls=detalle, spacing=8),
                    padding=ft.Padding(left=12, top=4, right=12, bottom=10),
                )
            ],
            bgcolor=config.SUPERFICIE,
            collapsed_bgcolor=config.SUPERFICIE,
            text_color=config.TEXTO_PRIMARIO,
            icon_color=config.NARANJA_SUAVE,
            collapsed_icon_color=config.NARANJA_SUAVE,
            collapsed_text_color=config.TEXTO_PRIMARIO,
            shape=forma,
            collapsed_shape=forma,
            tile_padding=ft.Padding(left=12, top=6, right=12, bottom=6),
            controls_padding=ft.Padding.all(0),
            min_tile_height=64,
        )
