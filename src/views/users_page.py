"""Vista del directorio de usuarios (US11).

Solo accesible para administradores y auditores. Muestra el nombre, el
usuario y el rol de cada cuenta, con estados de carga, error y reintento.
No permite editar datos.
"""

from __future__ import annotations

import asyncio

import flet as ft

import src.config as config
from src.controllers.audit_controller import AuditController
from src.controllers.auth_controller import AuthController
from src.controllers.user_controller import UserController
from src.models import Role
from src.models.user import UserDTO
from src.views.navigation import crear_barra_navegacion
from src.views.widgets import (
    avatar_codigo,
    insignia_rol,
    pantalla_acceso_denegado,
)

BORDE_SUAVE = ft.border.Border.all(width=1, color=config.BORDE)


class UsersPage:
    """Directorio de cuentas registradas en la API local."""

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
        self._usuarios_ctrl = UserController()
        self._usuarios: list[UserDTO] = []
        self._contenido = None
        self._contador = None

    # ------------------------------------------------------------------
    # Construccion de la vista
    # ------------------------------------------------------------------
    def build(self) -> ft.Container:
        """Construye el directorio; sin rol autorizado muestra bloqueo."""
        if not self._audit.puede_ver_usuarios(self._auth.current_role):
            return pantalla_acceso_denegado(
                "Esta seccion solo esta disponible para administradores y "
                "auditores.",
                self._on_home,
            )

        cabecera = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "USUARIOS",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_ATENUADO,
                        ),
                        ft.Text(
                            "Directorio de cuentas",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_PRIMARIO,
                        ),
                    ],
                    spacing=0,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            icon_color=config.NARANJA_SUAVE,
                            tooltip="Recargar usuarios",
                            on_click=self._on_cargar,
                        ),
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.GROUPS,
                                size=24,
                                color=config.NEGRO,
                            ),
                            width=46,
                            height=46,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=config.NARANJA,
                            border_radius=ft.BorderRadius.all(14),
                        ),
                    ],
                    spacing=4,
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
            "usuarios",
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
                        "Cargando usuarios...",
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
                        ft.Icons.PERSON_OFF,
                        size=42,
                        color=config.TEXTO_ATENUADO,
                    ),
                    ft.Text(
                        "No hay usuarios registrados.",
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
        """Descarga el directorio y lo pinta (solo con rol autorizado)."""
        if not self._audit.puede_ver_usuarios(self._auth.current_role):
            return

        self._contenido.content = self._estado_cargando()
        self._page.update()

        try:
            usuarios = await asyncio.to_thread(self._audit.usuarios)
        except Exception:
            self._contenido.content = self._estado_error(
                "No se pudo cargar el directorio de usuarios. "
                "Revisa tu conexion e intenta de nuevo."
            )
            self._page.update()
            return

        self._usuarios = usuarios
        self._pintar()

    def _on_cargar(self, e) -> None:
        self._page.run_task(self._cargar)

    def _pintar(self) -> None:
        ordenados = sorted(self._usuarios, key=lambda u: u.id)
        total = len(ordenados)
        self._contador.value = f"{total} cuenta(s) registrada(s)"

        if not ordenados:
            estado = self._estado_vacio()
        else:
            estado = ft.ListView(
                controls=[self._tarjeta_usuario(u) for u in ordenados],
                spacing=8,
                padding=ft.Padding(left=16, right=16, bottom=16),
                expand=True,
            )

        self._contenido.content = estado
        self._page.update()

    # ------------------------------------------------------------------
    # Tarjeta de cada usuario
    # ------------------------------------------------------------------
    def _dato(self, icono, valor: str) -> ft.Row:
        return ft.Row(
            controls=[
                ft.Icon(icono, size=15, color=config.NARANJA_SUAVE),
                ft.Text(
                    valor or "-",
                    size=12,
                    color=config.TEXTO_SECUNDARIO,
                    expand=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            spacing=8,
        )

    def _tarjeta_usuario(self, usuario: UserDTO) -> ft.Container:
        rol = Role.from_nombre(usuario.role)
        nombre = self._usuarios_ctrl.get_full_name(usuario).strip()
        nombre = nombre or usuario.username or f"Usuario #{usuario.id}"
        etiqueta_rol = self._usuarios_ctrl.get_role_label(rol, usuario.role)
        color_rol = self._usuarios_ctrl.get_role_color(rol)

        datos = ft.Column(
            controls=[
                self._dato(
                    ft.Icons.ALTERNATE_EMAIL,
                    f"@{usuario.username}" if usuario.username else "",
                ),
                self._dato(ft.Icons.BADGE, usuario.role or "Sin rol"),
                self._dato(ft.Icons.NUMBERS, f"ID {usuario.id}"),
            ],
            spacing=5,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            avatar_codigo(usuario.id, tamano=46),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        nombre,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=config.TEXTO_PRIMARIO,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    insignia_rol(etiqueta_rol, color_rol),
                                ],
                                spacing=5,
                                expand=True,
                            ),
                        ],
                        spacing=12,
                    ),
                    datos,
                ],
                spacing=10,
            ),
            bgcolor=config.SUPERFICIE,
            border_radius=ft.BorderRadius.all(12),
            border=BORDE_SUAVE,
            padding=ft.Padding.all(12),
        )
